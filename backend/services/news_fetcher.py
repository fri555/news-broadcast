"""Real RSS news aggregator — domestic Chinese sources."""
import hashlib
import asyncio
from datetime import datetime
from typing import Optional
import feedparser
import httpx

RSS_SOURCES = [
    {"name": "36氪", "url": "https://36kr.com/feed", "category": "科技"},
    {"name": "少数派", "url": "https://sspai.com/feed", "category": "科技·数码"},
    {"name": "虎嗅", "url": "https://www.huxiu.com/rss/0.xml", "category": "科技·商业"},
    {"name": "知乎每日精选", "url": "https://www.zhihu.com/rss", "category": "综合"},
    {"name": "IT之家", "url": "https://www.ithome.com/rss/", "category": "科技"},
    {"name": "Solidot", "url": "https://www.solidot.org/index.rss", "category": "科技"},
    {"name": "果壳", "url": "https://www.guokr.com/rss/", "category": "科普"},
    {"name": "爱范儿", "url": "https://www.ifanr.com/feed", "category": "科技"},
]


def parse_time(entry) -> str:
    try:
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            dt = datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            dt = datetime(*entry.updated_parsed[:6])
        else:
            return ""
        diff = datetime.now() - dt
        mins = int(diff.total_seconds() / 60)
        if mins < 1: return "刚刚"
        if mins < 60: return f"{mins}分钟前"
        hours = mins // 60
        if hours < 24: return f"{hours}小时前"
        return f"{hours // 24}天前"
    except Exception:
        return ""


def clean_html(html: str) -> str:
    import re
    clean = re.sub(r'<[^>]+>', '', html)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()[:200]


async def fetch_single_feed(source: dict) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(
                source["url"],
                headers={
                    "User-Agent": "NewsCast/0.1 RSS Reader (iPhone; CPU iPhone OS like Mac OS X)",
                    "Accept": "application/rss+xml, application/xml, text/xml, */*",
                },
            )
            if resp.status_code != 200:
                print(f"  [{source['name']}] HTTP {resp.status_code}")
                return []

        feed = feedparser.parse(resp.text)
        if not feed.entries:
            print(f"  [{source['name']}] No entries")
            return []

        items = []
        for entry in feed.entries[:5]:
            title = entry.get('title', '').strip()
            if not title or len(title) < 10:
                continue
            summary = entry.get('summary', '') or entry.get('description', '') or ''
            summary = clean_html(summary)
            if len(summary) < 20:
                summary = title

            item_id = hashlib.md5((source['name'] + title).encode()).hexdigest()[:12]
            items.append({
                "id": item_id,
                "category": f"{source['category']} · 快讯",
                "title": title,
                "summary": summary,
                "source": source["name"],
                "sourceUrl": entry.get('link', '#'),
                "publishedAt": parse_time(entry),
                "isRead": False,
            })

        print(f"  [{source['name']}] ✅ {len(items)} articles")
        return items
    except Exception as e:
        print(f"  [{source['name']}] ❌ {e}")
        return []


async def fetch_all_news() -> list[dict]:
    print(f"\n🔄 Fetching news from {len(RSS_SOURCES)} domestic sources...")
    results = await asyncio.gather(*[fetch_single_feed(s) for s in RSS_SOURCES], return_exceptions=True)

    all_items = []
    seen = set()
    for result in results:
        if isinstance(result, list):
            for item in result:
                if item["id"] not in seen:
                    seen.add(item["id"])
                    all_items.append(item)

    def sort_key(item):
        t = item["publishedAt"]
        if "分钟前" in t: return int(t.replace("分钟前", ""))
        if "小时前" in t: return int(t.replace("小时前", "")) * 60
        if "刚刚" == t: return 0
        if "天前" in t: return int(t.replace("天前", "")) * 1440
        return 99999

    all_items.sort(key=sort_key)
    print(f"✅ Total: {len(all_items)} unique articles\n")
    return all_items


_cached_news: list[dict] = []
_cache_time: Optional[datetime] = None
CACHE_TTL = 300


async def get_news(force_refresh: bool = False) -> list[dict]:
    global _cached_news, _cache_time
    now = datetime.now()
    if not force_refresh and _cached_news and _cache_time and (now - _cache_time).total_seconds() < CACHE_TTL:
        return _cached_news
    try:
        items = await fetch_all_news()
        if items:
            _cached_news = items
            _cache_time = now
            return items
    except Exception as e:
        print(f"News fetch failed: {e}")
    return _cached_news
