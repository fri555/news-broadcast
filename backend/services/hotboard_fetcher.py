"""
Hotboard fetcher — multi-source news aggregation with 3-tier fallback.
Data sources: uapis.cn hotboard API + NewsNow + RSS feeds.
"""
import re
import json
import hashlib
import asyncio
import logging
import urllib.request
import ssl
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlparse

import feedparser
import httpx
import certifi
from bs4 import BeautifulSoup

from config import (
    HOTBOARD_API, NEWSNOW_BASE_URL, ENABLE_NEWSNOW,
    MAX_ITEMS_PER_SOURCE, BATCH_LIMIT, NEWS_CACHE_TTL_HOURS,
)

logger = logging.getLogger(__name__)

# ── 热榜 API 数据源 ───────────────────────────────────────

HOTBOARD_SOURCES = {
    "weibo":    {"name": "微博",     "topics": ["综合", "社会"]},
    "zhihu":    {"name": "知乎",     "topics": ["知识", "综合"]},
    "bilibili": {"name": "B站",      "topics": ["游戏", "娱乐"]},
    "douyin":   {"name": "抖音",     "topics": ["生活", "娱乐"]},
    "toutiao":  {"name": "今日头条",  "topics": ["综合", "时政"]},
    "baidu":    {"name": "百度热搜",  "topics": ["综合", "社会"]},
    "36kr":     {"name": "36氪",     "topics": ["科技", "创业", "互联网"]},
    "thepaper": {"name": "澎湃新闻",  "topics": ["时政", "财经"]},
    "ithome":   {"name": "IT之家",   "topics": ["科技", "数码"]},
}

# 领域 → 对应的热榜平台
TOPIC_TO_SOURCES: dict[str, list[str]] = {}
for _sid, _info in HOTBOARD_SOURCES.items():
    for _t in _info["topics"]:
        TOPIC_TO_SOURCES.setdefault(_t, []).append(_sid)

SOURCE_CATALOG = [
    {"id": "36kr", "label": "36氪", "kind": "热榜", "trust": "高", "topics": ["科技", "创业", "互联网"], "description": "科技创投与产业新闻"},
    {"id": "thepaper", "label": "澎湃新闻", "kind": "热榜", "trust": "高", "topics": ["时政", "财经"], "description": "时政与深度报道"},
    {"id": "ithome", "label": "IT之家", "kind": "热榜", "trust": "高", "topics": ["科技", "数码"], "description": "数码、科技与产品动态"},
    {"id": "toutiao", "label": "今日头条", "kind": "热榜", "trust": "中", "topics": ["综合", "时政"], "description": "综合热闻聚合"},
    {"id": "baidu", "label": "百度热搜", "kind": "热榜", "trust": "中", "topics": ["综合", "社会"], "description": "大众关注热点"},
    {"id": "weibo", "label": "微博", "kind": "热榜", "trust": "中", "topics": ["综合", "社会"], "description": "社交媒体热议"},
    {"id": "zhihu", "label": "知乎", "kind": "热榜", "trust": "中", "topics": ["知识", "综合"], "description": "话题讨论与观点"},
    {"id": "bilibili", "label": "B站", "kind": "热榜", "trust": "中", "topics": ["游戏", "娱乐"], "description": "年轻化内容与视频热度"},
    {"id": "douyin", "label": "抖音", "kind": "热榜", "trust": "中", "topics": ["生活", "娱乐"], "description": "短视频热度内容"},
    {"id": "rss:AI", "label": "RSS · AI", "kind": "RSS", "trust": "高", "topics": ["AI"], "description": "AI 行业文章与分析"},
    {"id": "rss:科技", "label": "RSS · 科技", "kind": "RSS", "trust": "高", "topics": ["科技"], "description": "科技媒体深度内容"},
    {"id": "rss:财经", "label": "RSS · 财经", "kind": "RSS", "trust": "高", "topics": ["财经"], "description": "财经资讯与市场分析"},
    {"id": "rss:互联网", "label": "RSS · 互联网", "kind": "RSS", "trust": "中", "topics": ["互联网"], "description": "互联网行业观察"},
    {"id": "rss:游戏", "label": "RSS · 游戏", "kind": "RSS", "trust": "中", "topics": ["游戏"], "description": "游戏产业与产品动态"},
    {"id": "rss:数码", "label": "RSS · 数码", "kind": "RSS", "trust": "中", "topics": ["数码"], "description": "数码产品与评测"},
]

SOURCE_CATALOG_MAP = {item["id"]: item for item in SOURCE_CATALOG}

# ── RSS 补充数据源 ────────────────────────────────────────

RSS_FEEDS = {
    "AI": [
        "https://www.36kr.com/feed",
        "https://www.pingwest.com/feed",
    ],
    "科技": [
        "https://sspai.com/feed",
    ],
    "财经": [
        "https://wallstreetcn.com/news/global",
    ],
    "互联网": [
        "https://www.huxiu.com/rss/0.xml",
    ],
    "游戏": [
        "https://www.gcores.com/rss",
    ],
    "数码": [
        "https://sspai.com/feed",
    ],
}

# ── 静态兜底数据 ──────────────────────────────────────────

FALLBACK_NEWS = [
    {"id": "fb1", "title": "Apple 发布新一代 AI 芯片 M5 Ultra，端侧推理性能提升 3 倍",
     "summary": "采用全新 3nm+ 制程，神经网络引擎核心翻倍至 32 核，统一内存带宽达到 800GB/s。这意味着未来 MacBook Pro 可以在本地运行千亿参数大模型。",
     "source": "36氪", "topic": "科技", "sourceUrl": "#", "publishedAt": "15分钟前", "hot_value": "987654", "image": ""},
    {"id": "fb2", "title": "A股三大指数集体收涨，两市成交额突破万亿",
     "summary": "沪指涨 0.8%，深成指涨 1.2%，创业板指涨 2.1%，北向资金净流入超 80 亿元。半导体、AI 算力板块领涨。",
     "source": "证券时报", "topic": "财经", "sourceUrl": "#", "publishedAt": "30分钟前", "hot_value": "876543", "image": ""},
    {"id": "fb3", "title": "中国队 3:1 击败对手，世界杯预选赛再下一城",
     "summary": "凭借下半场两粒精彩进球，中国队在主场拿下关键三分，小组排名升至第二，出线形势大好。",
     "source": "央视体育", "topic": "综合", "sourceUrl": "#", "publishedAt": "1小时前", "hot_value": "765432", "image": ""},
    {"id": "fb4", "title": "OpenAI 推出 GPT-5，多模态推理能力大幅提升",
     "summary": "支持实时视频理解与复杂代码生成，API 价格下调 50%，上下文窗口扩展至 2M tokens，开发者生态迎来重大利好。",
     "source": "量子位", "topic": "AI", "sourceUrl": "#", "publishedAt": "2小时前", "hot_value": "654321", "image": ""},
    {"id": "fb5", "title": "特斯拉 Optimus 机器人正式量产，售价 2 万美元",
     "summary": "首批 1000 台交付工厂使用，马斯克称明年产能将提升至 10 万台。机器人可执行装配、搬运等 50+ 种工厂任务。",
     "source": "爱范儿", "topic": "科技", "sourceUrl": "#", "publishedAt": "3小时前", "hot_value": "543210", "image": ""},
    {"id": "fb6", "title": "央行宣布降准 0.5 个百分点，释放长期流动性约 1 万亿",
     "summary": "此次降准旨在支持实体经济发展，降低社会融资成本。分析师预计后续还有进一步宽松空间。",
     "source": "央行官网", "topic": "财经", "sourceUrl": "#", "publishedAt": "2小时前", "hot_value": "987123", "image": ""},
    {"id": "fb7", "title": "华为发布鸿蒙 5.0，全场景分布式操作系统再进化",
     "summary": "鸿蒙 5.0 实现手机、平板、车机、IoT 设备统一架构，开发者数量突破 800 万，生态初具规模。",
     "source": "IT之家", "topic": "科技", "sourceUrl": "#", "publishedAt": "4小时前", "hot_value": "876111", "image": ""},
    {"id": "fb8", "title": "全球气候峰会达成新共识：2035 年碳减排目标提高至 60%",
     "summary": "190 多个国家签署新协议，发达国家承诺每年提供 5000 亿美元气候融资支持发展中国家转型。",
     "source": "新华社", "topic": "时政", "sourceUrl": "#", "publishedAt": "5小时前", "hot_value": "765888", "image": ""},
    {"id": "fb9", "title": "《黑神话：悟空 2》正式公布，预告片播放量破亿",
     "summary": "游戏科学宣布续作将于 2027 年发售，采用虚幻引擎 5.5 开发，新增开放世界探索和多人合作模式。",
     "source": "游戏葡萄", "topic": "游戏", "sourceUrl": "#", "publishedAt": "3小时前", "hot_value": "999555", "image": ""},
    {"id": "fb10", "title": "字节跳动旗下 AI 教育产品全球用户突破 2 亿",
     "summary": "该产品利用大语言模型提供个性化学习路径，覆盖数学、编程、语言等 8 个学科，已进入 30 个国家市场。",
     "source": "晚点财经", "topic": "AI", "sourceUrl": "#", "publishedAt": "6小时前", "hot_value": "654987", "image": ""},
    {"id": "fb11", "title": "NASA 宣布火星样本返回任务提前至 2030 年",
     "summary": "与 SpaceX 合作使用星舰作为返回载具，预计将带回 500 克火星岩石和土壤样本，有望揭开火星生命之谜。",
     "source": "环球科学", "topic": "科技", "sourceUrl": "#", "publishedAt": "1小时前", "hot_value": "888222", "image": ""},
    {"id": "fb12", "title": "2026 年高校毕业生人数创新高，AI 相关岗位增长 45%",
     "summary": "教育部数据显示今年高校毕业生达 1200 万，AI 训练师、提示工程师等新兴岗位需求旺盛。",
     "source": "人民日报", "topic": "社会", "sourceUrl": "#", "publishedAt": "4小时前", "hot_value": "777333", "image": ""},
]


# ── 工具函数 ──────────────────────────────────────────────

def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", str(title)).strip()


def _urllib_fetch(url: str) -> dict:
    """同步 HTTP GET，返回 JSON dict"""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; NewsCast/1.0)",
        "Accept": "application/json",
    })
    context = ssl.create_default_context(cafile=certifi.where())
    with urllib.request.urlopen(req, timeout=5, context=context) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_source_catalog() -> list[dict]:
    """返回可选信息源目录。"""
    return list(SOURCE_CATALOG)


def _source_label(source_id: str) -> str:
    meta = SOURCE_CATALOG_MAP.get(source_id)
    return meta["label"] if meta else source_id


async def _fetch_article_context(url: str) -> dict:
    """尽量抓取原文正文，用于补全标题党和过短摘要。"""
    if not url or not url.startswith(("http://", "https://")):
        return {}

    try:
        async with httpx.AsyncClient(
            timeout=4.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; NewsCast/1.0)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        ) as client:
            resp = await client.get(url)
        if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", "").lower():
            return {}

        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        def pick_meta(names: list[str]) -> str:
            for name in names:
                meta = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
                if meta and meta.get("content"):
                    content = str(meta.get("content")).strip()
                    if content:
                        return content
            return ""

        title = pick_meta(["og:title", "twitter:title"]) or (soup.title.get_text(strip=True) if soup.title else "")
        desc = pick_meta(["og:description", "twitter:description", "description"])

        article_nodes = []
        for selector in ["article", "main", '[role="main"]']:
            node = soup.select_one(selector)
            if node:
                article_nodes.append(node)

        paragraphs: list[str] = []
        if article_nodes:
            for node in article_nodes:
                for p in node.find_all("p"):
                    text = p.get_text(" ", strip=True)
                    if len(text) >= 24:
                        paragraphs.append(text)
        else:
            for p in soup.find_all("p"):
                text = p.get_text(" ", strip=True)
                if len(text) >= 24:
                    paragraphs.append(text)

        body = "\n".join(paragraphs[:12]).strip()
        body = re.sub(r"\s+", " ", body)
        if len(body) < 120 and desc:
            body = desc

        if not title and not body and not desc:
            return {}

        return {
            "article_title": title[:120],
            "article_excerpt": (body or desc)[:900],
            "article_description": desc[:500],
            "article_length": len(body or desc),
            "article_domain": urlparse(url).netloc,
        }
    except Exception:
        return {}


# ── 热榜 API 抓取（uapis.cn）───────────────────────────────

async def fetch_hotboard(source_id: str, max_items: int = 10) -> list[dict]:
    """从 uapis.cn 热榜 API 抓取指定平台的实时热门"""
    source_meta = HOTBOARD_SOURCES.get(source_id)
    if not source_meta:
        return []

    url = f"{HOTBOARD_API}?type={source_id}"
    try:
        loop = asyncio.get_event_loop()
        raw_data = await asyncio.wait_for(
            loop.run_in_executor(None, lambda: _urllib_fetch(url)),
            timeout=5,
        )
        items = raw_data.get("list", [])
        if not items:
            return []

        source_name = source_meta["name"]
        topic_hint = source_meta["topics"][0] if source_meta["topics"] else "综合"
        news = []
        for item in items[:max_items]:
            title = item.get("title", "").strip()
            if not title:
                continue
            item_url = item.get("url", "")
            hot = item.get("hot_value", "")
            extra = item.get("extra", {})

            # 尝试从多个字段获取描述
            desc = ""
            if isinstance(extra, dict):
                desc = extra.get("desc", "") or extra.get("description", "") or extra.get("content", "")
            if not desc:
                desc = item.get("desc", "") or item.get("description", "") or item.get("content", "")

            summary = desc[:500] if desc else ""

            news.append({
                "id": hashlib.md5(f"{source_id}:{title}".encode()).hexdigest()[:12],
                "title": title,
                "summary": summary,
                "read_aloud": "",
                "source": source_name,
                "sourceUrl": str(item_url),
                "topic": topic_hint,
                "hot_value": str(hot),
            })
        return news
    except Exception as e:
        logger.warning(f"Hotboard fetch failed for {source_id}: {e}")
        return []


# ── NewsNow 数据源 ─────────────────────────────────────────

async def fetch_newsnow(source_id: str, max_items: int = 8) -> list[dict]:
    """从 NewsNow 抓取指定平台热榜"""
    if not ENABLE_NEWSNOW:
        return []

    source_meta = HOTBOARD_SOURCES.get(source_id)
    if not source_meta:
        return []

    url = f"{NEWSNOW_BASE_URL}/api/s/{source_id}"
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return []
            data = resp.json()

        items = data.get("data", []) if isinstance(data, dict) else []
        source_name = source_meta["name"]
        topic_hint = source_meta["topics"][0] if source_meta["topics"] else "综合"

        news = []
        for item in items[:max_items]:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or item.get("name") or "").strip()
            if not title:
                continue
            extra = item.get("extra", {})
            desc = ""
            if isinstance(extra, dict):
                desc = (
                    extra.get("desc") or extra.get("description")
                    or extra.get("info") or extra.get("hover") or ""
                )
            desc = desc or item.get("desc") or item.get("description") or item.get("summary") or ""
            item_url = item.get("url") or item.get("mobileUrl") or item.get("link") or ""
            hot = item.get("hot") or item.get("hotValue") or item.get("hot_value") or item.get("score") or ""

            news.append({
                "id": hashlib.md5(f"newsnow:{source_id}:{title}".encode()).hexdigest()[:12],
                "title": title,
                "summary": str(desc).strip()[:500] if desc else "",
                "read_aloud": "",
                "source": f"NewsNow · {source_name}",
                "sourceUrl": str(item_url),
                "topic": topic_hint,
                "hot_value": str(hot),
            })
        return news
    except Exception as e:
        logger.warning(f"NewsNow fetch failed for {source_id}: {e}")
        return []


# ── RSS 补充 ──────────────────────────────────────────────

async def fetch_rss_feed(topic: str, url: str, max_items: int = 5) -> list[dict]:
    """抓取单个 RSS 源"""
    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={
                    "User-Agent": "NewsCast/1.0 RSS Reader",
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                },
            )
            if resp.status_code != 200:
                return []

        loop = asyncio.get_event_loop()
        feed = await asyncio.wait_for(
            loop.run_in_executor(None, feedparser.parse, resp.text),
            timeout=5,
        )

        news = []
        for entry in feed.entries[:max_items]:
            raw = entry.get("summary", entry.get("description", ""))
            raw = re.sub(r"<[^>]+>", "", raw).strip()[:500]
            news.append({
                "id": hashlib.md5(entry.get("link", "").encode()).hexdigest()[:12],
                "title": entry.get("title", "无标题"),
                "summary": raw,
                "read_aloud": "",
                "source": feed.feed.get("title", topic),
                "sourceUrl": entry.get("link", ""),
                "topic": topic,
            })
            if len(news) >= max_items:
                break
        return news
    except Exception as e:
        logger.warning(f"RSS fetch failed {url}: {e}")
        return []


async def fetch_all_rss_for_topic(topic: str, max_items: int = 5) -> list[dict]:
    """抓取某个领域的所有 RSS 源"""
    urls = RSS_FEEDS.get(topic, [])
    if not urls:
        return []
    results = await asyncio.gather(*[fetch_rss_feed(topic, u, max_items) for u in urls])
    all_items = []
    for r in results:
        if isinstance(r, list):
            all_items.extend(r)
    return all_items


async def enrich_with_article_context(items: list[dict], max_items: int = 4) -> list[dict]:
    """给部分新闻补抓原文正文，避免只有标题和短摘要。"""
    if not items:
        return items

    sem = asyncio.Semaphore(3)

    async def safe_enrich(item: dict, idx: int):
        async with sem:
            if idx >= max_items:
                return item
            url = str(item.get("sourceUrl", "")).strip()
            summary = str(item.get("summary", "")).strip()
            source = str(item.get("source", "")).strip()
            if not url or url == "#" or not url.startswith(("http://", "https://")):
                return item
            if len(summary) >= 220 and source not in {"36氪", "澎湃新闻", "IT之家", "环球科学", "新华社", "人民日报", "央行官网"}:
                return item

            context = await _fetch_article_context(url)
            if not context:
                return item

            item["article_context"] = context
            excerpt = context.get("article_excerpt", "").strip()
            if excerpt and len(summary) < 160:
                item["summary"] = excerpt[:500]
            if context.get("article_title") and len(item.get("title", "")) < 12:
                item["title"] = context["article_title"]
            return item

    return await asyncio.gather(*[safe_enrich(dict(item), i) for i, item in enumerate(items)])


# ── 去重 ──────────────────────────────────────────────────

def dedup_append(
    items: list[dict],
    target: list[dict],
    seen_urls: set[str],
    seen_titles: set[str],
):
    """按 URL + 标题去重后追加到目标列表"""
    for item in items:
        url = _normalize_title(item.get("sourceUrl", ""))
        title = _normalize_title(item.get("title", ""))
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)
        target.append(item)


# ── 缓存 ──────────────────────────────────────────────────

_news_cache: dict[str, dict] = {}
_cache_lock = asyncio.Lock()


def _cache_fresh(entry: Optional[dict], ttl_hours: float) -> bool:
    if not entry:
        return False
    return datetime.now() - entry["ts"] < timedelta(hours=ttl_hours)


def _news_cache_key(selected: list[str], limit: int = 0) -> str:
    batch = limit if limit > 0 else BATCH_LIMIT
    return f"{','.join(sorted(selected))}|{batch}"


def _news_cache_key_with_sources(selected_topics: list[str], selected_sources: list[str], limit: int = 0) -> str:
    batch = limit if limit > 0 else BATCH_LIMIT
    return f"{','.join(sorted(selected_topics))}|{','.join(sorted(selected_sources))}|{batch}"


async def get_cached_news(key: str) -> Optional[dict]:
    async with _cache_lock:
        entry = _news_cache.get(key)
        if _cache_fresh(entry, NEWS_CACHE_TTL_HOURS):
            data = dict(entry["data"])
            data["cached"] = True
            data["cache_time"] = entry["ts"].isoformat(timespec="seconds")
            return data
    return None


async def set_cached_news(key: str, data: dict):
    async with _cache_lock:
        _news_cache[key] = {"data": data, "ts": datetime.now()}


# ── 主抓取流水线 ──────────────────────────────────────────

async def fetch_all_news(
    selected_topics: list[str],
    selected_sources: Optional[list[str]] = None,
    limit: int = 0,
    force_refresh: bool = False,
) -> dict:
    """
    主入口：按领域聚合热榜 + NewsNow + RSS，AI 层面的富化由 ai 服务完成。
    三层降级：热榜双源 → RSS → 静态兜底。
    """
    batch = limit if limit > 0 else BATCH_LIMIT
    selected_sources = [s for s in (selected_sources or []) if s in SOURCE_CATALOG_MAP]
    key = _news_cache_key_with_sources(selected_topics, selected_sources, batch)

    # 检查缓存
    if not force_refresh:
        cached = await get_cached_news(key)
        if cached:
            return cached

    # 找到领域对应的热榜平台
    needed_sources: set[str] = set()
    rss_topics: set[str] = set()
    if selected_sources:
        for source_id in selected_sources:
            if source_id.startswith("rss:"):
                topic = source_id.split("rss:", 1)[1]
                if topic in RSS_FEEDS:
                    rss_topics.add(topic)
            else:
                needed_sources.add(source_id)
    else:
        for t in selected_topics:
            needed_sources.update(TOPIC_TO_SOURCES.get(t, []))
            if t in RSS_FEEDS:
                rss_topics.add(t)

    # 第一层：NewsNow + uapis 双源并发
    source_tasks = {}
    for sid in needed_sources:
        source_tasks[f"newsnow:{sid}"] = fetch_newsnow(sid, max_items=MAX_ITEMS_PER_SOURCE)
        source_tasks[f"uapis:{sid}"] = fetch_hotboard(sid, max_items=MAX_ITEMS_PER_SOURCE)

    source_results = {}
    if source_tasks:
        results = await asyncio.gather(*source_tasks.values(), return_exceptions=True)
        for key_name, r in zip(source_tasks.keys(), results):
            if isinstance(r, list):
                source_results[key_name] = r

    # 汇总去重
    all_news: list[dict] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    for key_name in sorted(source_results.keys()):
        dedup_append(source_results[key_name], all_news, seen_urls, seen_titles)

    # 第二层：RSS 补充（热榜不够时）
    if len(all_news) < batch:
        logger.info(f"Hotboard returned {len(all_news)} items, supplementing with RSS...")
        rss_batch = batch - len(all_news)
        for topic in sorted(rss_topics or set(selected_topics)):
            if len(all_news) >= batch:
                break
            rss_items = await fetch_all_rss_for_topic(topic, max_items=5)
            dedup_append(rss_items, all_news, seen_urls, seen_titles)
        all_news = all_news[:batch]

    # 第三层：静态兜底
    if not all_news:
        logger.warning("All sources failed, using fallback data")
        all_news = [dict(f) for f in FALLBACK_NEWS]

    # 先补抓少量原文，再走 AI 富化；主链路只做轻量补全，避免首次加载过慢
    all_news = await enrich_with_article_context(all_news[:4]) + all_news[4:]

    # 确保 summary 不为空
    for item in all_news:
        if not item.get("summary") or not item["summary"].strip():
            item["summary"] = item.get("title", "暂无内容")

    # 按可信度和内容完整度做一次排序，优先展示更像“完整新闻”的条目
    def _score(item: dict) -> tuple:
        source = str(item.get("source", ""))
        title = str(item.get("title", ""))
        summary = str(item.get("summary", ""))
        detail = item.get("detail") if isinstance(item.get("detail"), dict) else {}
        richness = detail.get("content_richness", "thin") if isinstance(detail, dict) else "thin"
        source_rank = 3 if source in {"新华社", "人民日报", "央行官网", "澎湃新闻", "36氪", "IT之家"} else 2 if "RSS" in source or source.startswith("NewsNow") else 1
        richness_rank = {"rich": 3, "partial": 2, "thin": 1}.get(richness, 1)
        text_rank = 2 if len(summary) >= 140 else 1 if len(summary) >= 60 else 0
        title_rank = 1 if len(title) <= 24 else 0
        return (source_rank, richness_rank, text_rank, title_rank)

    all_news = sorted(all_news, key=_score, reverse=True)

    source_type = "newsnow+uapis" if source_results else "rss"

    result = {"news": list(all_news), "source": source_type, "topics": selected_topics}
    await set_cached_news(key, result)
    return result
