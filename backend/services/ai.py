"""
NewsCast AI service — news enrichment, read-aloud generation, and dual-host broadcast scripts.
Ported and enhanced from news-companion.
"""
import re
import json
import asyncio
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional

from openai import AsyncOpenAI

from config import (
    API_KEY, API_BASE_URL, AI_MODEL,
    VOICE_A, VOICE_B, BROADCAST_CACHE_TTL_HOURS,
    OPENAI_TTS_VOICE_A, OPENAI_TTS_VOICE_B, TTS_PROVIDER,
)

logger = logging.getLogger(__name__)


def has_ai() -> bool:
    return bool(API_KEY and API_KEY not in ("", "your_api_key_here"))


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=API_KEY, base_url=API_BASE_URL)


# ── AI 批量富化：主题分类 + 新闻解读 ───────────────────────

SYSTEM_ENRICH = """你是一个资深新闻编辑。请对以下热榜新闻条目做三件事：
1. 为每条新闻重新分类到最合适的领域（从给定列表中选一个）
2. 生成 80-120 字卡片摘要，适合快速扫读
3. 生成结构化详情，让用户点进卡片后能看到比摘要更深的信息

【领域列表】：{topics}、其他

返回 JSON 数组，每条格式：
{
  "index": 序号,
  "topic": "领域",
  "summary": "80-120字卡片摘要",
  "detail": {
    "one_liner": "一句话说明发生了什么",
    "key_facts": ["关键事实1", "关键事实2", "关键事实3"],
    "background": "背景解释，说明为什么重要",
    "impact": "影响分析或后续关注点",
    "source_notes": "基于标题/摘要/来源判断的信息充分度说明",
    "content_richness": "rich|partial|thin"
  }
}

如果参考信息不足，不要编造具体数据；content_richness 填 thin，并在 source_notes 中说明需要查看原文确认。

只返回 JSON 数组，不要其他内容。"""


def build_fallback_detail(item: dict) -> dict:
    """在 AI 不可用或信息不足时提供明确的详情结构，而不是重复摘要。"""
    title = item.get("title", "").strip()
    summary = item.get("summary", "").strip()
    source = item.get("source", "当前来源")
    topic = item.get("topic", "综合")
    has_context = bool(summary and summary != title and len(summary) > 20)

    return {
        "one_liner": summary[:80] if has_context else title,
        "key_facts": [
            f"来源：{source}",
            f"领域：{topic}",
            "当前数据主要来自热榜/RSS条目，完整事实需要结合原文确认。",
        ],
        "background": (
            f"这条新闻被归入{topic}领域。当前摘要提供了初步上下文，但还缺少完整原文、相关方回应和更多来源交叉验证。"
            if has_context else
            f"这条新闻目前只有标题级信息，暂时无法可靠展开背景。"
        ),
        "impact": "建议先查看原文链接；后续版本会在后台抓取正文和搜索补充材料后生成更完整的影响分析。",
        "source_notes": "信息充分度有限：当前详情由已有标题、摘要和来源生成，未完成多源交叉验证。",
        "content_richness": "partial" if has_context else "thin",
    }


async def enrich_hotboard_items(items: list[dict], target_topics: list[str]) -> list[dict]:
    """用 AI 对热榜条目做主题分类 + 生成详细摘要"""
    if not items:
        return items
    if not has_ai():
        for item in items:
            item["detail"] = build_fallback_detail(item)
        return items

    # 构造批量处理 prompt
    item_lines = []
    for i, item in enumerate(items):
        existing_desc = item.get("summary", "")
        if existing_desc and existing_desc != item.get("title", ""):
            item_lines.append(f"{i+1}. [{item.get('source','')}] {item['title']}（参考：{existing_desc[:100]}）")
        else:
            item_lines.append(f"{i+1}. [{item.get('source','')}] {item['title']}")

    topics_str = "、".join(target_topics) if target_topics else "综合"
    items_text = "\n".join(item_lines)

    prompt = (
        f"以下是今日热榜新闻，共 {len(items)} 条。请逐条做领域分类和解读。\n\n"
        f"【领域列表】：{topics_str}、其他\n\n"
        f"【新闻列表】：\n{items_text}\n\n"
        f"返回 JSON 数组，每条格式：\n"
        f'{{"index": 序号(数字), "topic": "领域", "summary": "80-120字卡片摘要", '
        f'"detail": {{"one_liner": "一句话结论", "key_facts": ["事实1", "事实2", "事实3"], '
        f'"background": "背景解释", "impact": "影响分析", "source_notes": "信息充分度说明", '
        f'"content_richness": "rich|partial|thin"}}}}\n\n'
        f"如果信息不足，不要编造具体数据；请把 content_richness 设为 thin 或 partial。\n\n"
        f"只返回 JSON 数组，不要其他内容。"
    )

    try:
        client = _get_client()
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model=AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.5,
            ),
            timeout=30,
        )
        content = resp.choices[0].message.content.strip()

        # 尝试提取 JSON 数组
        json_match = re.search(r"\[.*\]", content, re.DOTALL)
        if json_match:
            enriched_list = json.loads(json_match.group())
            enriched_map = {}
            for entry in enriched_list:
                idx = entry.get("index", 0) - 1  # 转为 0-based
                if 0 <= idx < len(items):
                    enriched_map[idx] = entry

            for i, item in enumerate(items):
                if i in enriched_map:
                    entry = enriched_map[i]
                    item["topic"] = entry.get("topic", item.get("topic", "综合"))
                    item["summary"] = entry.get("summary", item.get("summary", ""))
                    detail = entry.get("detail")
                    if isinstance(detail, dict):
                        item["detail"] = detail
    except Exception as e:
        logger.warning(f"AI enrichment failed: {e}, using original data")

    for item in items:
        if not isinstance(item.get("detail"), dict) or not item.get("detail"):
            item["detail"] = build_fallback_detail(item)

    return items


# ── AI 口语化播报文本 ─────────────────────────────────────

async def gen_read_aloud(index: int, title: str, raw_summary: str) -> str:
    """生成适合语音播报的口语化文本"""
    if not has_ai():
        clean = re.sub(r"\s+", " ", raw_summary).strip()
        if clean:
            return f"第{index}条。{title}。{clean[:150]}"
        else:
            return f"第{index}条。{title}。"

    try:
        client = _get_client()
        idx_str = f"第{index}条"
        prompt = (
            "请将下面这条新闻改写成适合语音播报的口语化文本，要求像一位自然、有温度的新闻陪伴助手在讲给朋友听：\n"
            f"1. 以「{idx_str}」开头\n"
            "2. 不要像机器人读稿，要有轻微起伏和解释感\n"
            "3. 包含关键事实和细节，90-130字\n"
            "4. 可以使用逗号、顿号和短句制造自然停顿，但不要用括号、书名号或 markdown\n"
            "5. 只输出改写后的文本，不要其他内容\n\n"
            f"标题：{title}\n"
            f"内容：{raw_summary[:500]}"
        )
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model=AI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5,
            ),
            timeout=15,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"gen_read_aloud failed idx {index}: {e}")
        clean = re.sub(r"\s+", " ", raw_summary).strip()
        if clean:
            return f"第{index}条。{title}。{clean[:150]}"
        else:
            return f"第{index}条。{title}。"


async def enrich_with_read_aloud(news_items: list[dict]) -> list[dict]:
    """并发生成所有新闻条目的口语播报文本"""
    sem = asyncio.Semaphore(5)

    async def safe_gen(idx, item):
        async with sem:
            try:
                result = await gen_read_aloud(idx + 1, item["title"], item.get("summary", ""))
                if result and result.strip():
                    item["read_aloud"] = result.strip()
            except Exception as e:
                logger.warning(f"gen_read_aloud failed idx {idx}: {e}")
            # 兜底
            if not item.get("read_aloud") or not item["read_aloud"].strip():
                clean = re.sub(r"\s+", " ", item.get("summary", "")).strip()
                if clean:
                    item["read_aloud"] = f"第{idx+1}条。{item['title']}。{clean[:150]}"
                else:
                    item["read_aloud"] = f"第{idx+1}条。{item['title']}。"
            return item

    return await asyncio.gather(*[safe_gen(i, item) for i, item in enumerate(news_items)])


# ── 双主播播报脚本生成 ────────────────────────────────────

_broadcast_cache: dict[str, dict] = {}
_broadcast_cache_lock = asyncio.Lock()


def _broadcast_voice_a() -> str:
    return OPENAI_TTS_VOICE_A if TTS_PROVIDER == "openai" else VOICE_A


def _broadcast_voice_b() -> str:
    return OPENAI_TTS_VOICE_B if TTS_PROVIDER == "openai" else VOICE_B


def _broadcast_cache_key(news_items: list[dict]) -> str:
    basis = [
        {
            "id": item.get("id", ""),
            "title": item.get("title", ""),
            "summary": item.get("summary", "")[:240],
        }
        for item in news_items
    ]
    raw = json.dumps(basis, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def parse_broadcast_script(raw: str) -> list[dict]:
    """解析 AI 生成的双主播播报脚本"""
    lines = []
    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^\[([AB])\]\s*(.+)$', line)
        if m:
            lines.append({"speaker": m.group(1), "text": m.group(2).strip()})
    return lines


def _build_fallback_script(news_items: list[dict]) -> list[dict]:
    """无 AI 时的兜底脚本"""
    lines = [
        {"speaker": "A", "text": "大家好，欢迎收听 NewsCast 新闻播报，我是小暖。"},
        {"speaker": "B", "text": "我是小明，今天由我们两位为大家播报新闻。"},
    ]
    for i, item in enumerate(news_items):
        title = item.get("title", "")
        summary = item.get("summary", "")[:200]
        topic = item.get("topic", "")
        if i % 2 == 0:
            lines.append({"speaker": "A", "text": f"接下来看一条{topic}领域的消息。{title}。"})
            lines.append({"speaker": "B", "text": f"对，{summary}"})
        else:
            lines.append({"speaker": "B", "text": f"再来看下一条。{title}。"})
            lines.append({"speaker": "A", "text": f"没错，{summary}"})
    lines.append({"speaker": "A", "text": "以上就是今天的全部新闻了。"})
    lines.append({"speaker": "B", "text": "感谢收听 NewsCast 新闻播报，我们下次再见。"})
    lines.append({"speaker": "A", "text": "再见！"})
    return lines


async def generate_broadcast_script(news_items: list[dict]) -> dict:
    """用 AI 生成双主播对话式新闻播报脚本"""
    if not has_ai():
        lines = _build_fallback_script(news_items)
    else:
        # 构造新闻素材文本
        news_parts = []
        for i, item in enumerate(news_items[:10]):
            news_parts.append(
                f"{i+1}. [{item.get('topic', '综合')}] {item.get('title', '')}\n"
                f"   摘要：{item.get('summary', '')[:200]}"
            )
        news_text = "\n\n".join(news_parts)

        prompt = (
            "你是一个优秀的广播节目制作人，请根据下面的新闻素材，写一份双主播对话式新闻播报脚本。\n\n"
            "【主播设定】\n"
            "- 主播A：晓晓（女），专业知识扎实，声音温暖有亲和力，负责新闻解读和深度分析\n"
            "- 主播B：云希（男），活泼风趣，负责新闻播报和轻松评论\n"
            "- 节目名称：NewsCast 新闻播报\n"
            "- 目标时长：15-20分钟\n\n"
            "【脚本要求】\n"
            "1. 开头：两位主播简短问候，介绍今日新闻概览\n"
            "2. 主体：每条新闻由两位主播交替播报和评论\n"
            "   - 不是简单读稿，要有互动和观点交流\n"
            "   - 适当补充背景知识和个人见解\n"
            "   - 新闻之间有自然过渡，必要时补一句承上启下的话\n"
            "3. 结尾：总结今日重点，与听众告别\n"
            "4. 语言风格：口语化、自然流畅，有轻微情绪起伏，像真正的电台节目，但不要油腻或夸张\n"
            "5. 总字数4500-6000字，目标时长 15-20 分钟，15 分钟是最低要求\n\n"
            "【输出格式】\n"
            "每行以 [A] 或 [B] 开头表示说话的主播，后面是台词内容。\n"
            "严格遵循此格式，不要加其他标记或说明。\n\n"
            f"【新闻素材】\n{news_text}"
        )

        try:
            client = _get_client()
            resp = await asyncio.wait_for(
                client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.7,
                ),
                timeout=60,
            )
            raw = resp.choices[0].message.content.strip()
            lines = parse_broadcast_script(raw)

            # 解析结果至少要有 6 行才像脚本
            if len(lines) < 6:
                logger.warning("AI broadcast script too short, using fallback")
                lines = _build_fallback_script(news_items)
        except Exception as e:
            logger.warning(f"AI broadcast generation failed: {e}")
            lines = _build_fallback_script(news_items)

    total_chars = sum(len(l["text"]) for l in lines)
    return {
        "script": lines,
        "voice_a": _broadcast_voice_a(),
        "voice_b": _broadcast_voice_b(),
        "total_chars": total_chars,
        "estimated_minutes": round(total_chars / 180, 1),
    }


async def get_or_generate_broadcast(news_items: list[dict], force_refresh: bool = False) -> dict:
    """获取缓存或生成新的播报脚本"""
    key = _broadcast_cache_key(news_items)

    async with _broadcast_cache_lock:
        cached = _broadcast_cache.get(key)
        stale = datetime.now() - cached["ts"] >= timedelta(hours=BROADCAST_CACHE_TTL_HOURS) if cached else True
        if not force_refresh and cached and not stale:
            data = dict(cached["data"])
            data["cached"] = True
            data["cache_time"] = cached["ts"].isoformat(timespec="seconds")
            return data

    data = await generate_broadcast_script(news_items)

    async with _broadcast_cache_lock:
        _broadcast_cache[key] = {"data": data, "ts": datetime.now()}

    result = dict(data)
    result["cached"] = False
    return result


# ── AI 追问（增强版）──────────────────────────────────────

SYSTEM_CHAT = """你是一个新闻陪伴助手，名叫「小暖」，正在和用户一起听新闻。

## 你的角色
- 名字叫「小暖」，性格亲和温暖，像一个知识渊博的朋友
- 专精于新闻解读和分析

## 回答要求
- 口语化、对话式语气
- 80-150字（适合语音播放）
- 可以补充背景知识，但不要长篇大论
- 不要用 markdown 格式
- 基于当前新闻内容来回答，不要编造事实"""


async def chat_with_news(question: str, news_title: str, news_context: str, history: list[dict] = None) -> str:
    """基于新闻上下文的 AI 追问"""
    if not has_ai():
        return "AI 服务未配置，请联系管理员设置有效的 API Key。\n\n💡 配置后即可进行语音追问、深度解读等功能。"

    client = _get_client()
    system_prompt = (
        f"{SYSTEM_CHAT}\n\n"
        f"当前新闻：\n标题：{news_title}\n内容：{news_context[:1000]}\n\n"
    )

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": question})

    try:
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model=AI_MODEL,
                messages=messages,
                max_tokens=300,
                temperature=0.7,
            ),
            timeout=20,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        return "抱歉，AI 服务暂时不可用，请稍后重试。"
