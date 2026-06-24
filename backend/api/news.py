"""
News API — multi-source hotboard aggregation + AI enrichment + topic filtering.
"""
import logging
from fastapi import APIRouter, Query, HTTPException

from services.hotboard_fetcher import (
    fetch_all_news,
    TOPIC_TO_SOURCES,
    RSS_FEEDS,
    get_source_catalog,
    enrich_with_article_context,
)
from services.ai import enrich_hotboard_items, enrich_with_read_aloud, has_ai, build_fallback_detail
from services.snapshots import read_news_snapshot, write_news_snapshot
from config import BATCH_LIMIT, DEFAULT_TOPICS

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/news", tags=["news"])

# 所有可用领域
ALL_TOPICS = sorted(set(list(TOPIC_TO_SOURCES.keys()) + list(RSS_FEEDS.keys())))


def _normalize_topics(topics: str = "") -> list[str]:
    """将逗号分隔的领域字符串规范化为列表"""
    if topics:
        return [t.strip() for t in topics.split(",") if t.strip() in ALL_TOPICS]
    return [t for t in DEFAULT_TOPICS if t in ALL_TOPICS]


def _normalize_sources(sources: str = "") -> list[str]:
    if not sources:
        return []
    valid = {item["id"] for item in get_source_catalog()}
    return [s.strip() for s in sources.split(",") if s.strip() in valid]


@router.get("/topics")
async def get_topics():
    """返回所有可用领域及推荐默认选中"""
    return {
        "all": ALL_TOPICS,
        "defaults": [t for t in DEFAULT_TOPICS if t in ALL_TOPICS],
    }


@router.get("/catalog")
async def get_sources():
    """返回所有可选信息源。"""
    return {
        "sources": get_source_catalog(),
    }


@router.get("")
async def get_news(
    topics: str = "",
    sources: str = "",
    limit: int = Query(default=0, ge=0, le=50),
    refresh: bool = False,
):
    """
    获取新闻列表（主接口）。
    - topics: 逗号分隔的领域，如 "科技,AI,财经"
    - limit: 返回条数，默认 10
    - refresh: 强制刷新缓存
    """
    selected = _normalize_topics(topics)
    selected_sources = _normalize_sources(sources)
    batch = limit if limit > 0 else BATCH_LIMIT

    if not refresh:
        snapshot = read_news_snapshot(selected + selected_sources, batch)
        if snapshot and snapshot.get("news"):
            return snapshot

    try:
        result = await fetch_all_news(selected, selected_sources, limit, force_refresh=refresh)
    except Exception as e:
        logger.error(f"News fetch failed: {e}")
        raise HTTPException(503, "所有数据源均暂时不可用，请稍后重试")

    all_news = result.get("news", [])

    # AI 富化：主题分类 + 新闻解读
    if has_ai() and all_news:
        enriched = await enrich_hotboard_items(all_news[:5], selected)
        all_news = enriched + all_news[5:]

    # 按用户选的主题过滤
    if selected:
        filtered = [item for item in all_news if item.get("topic", "") in selected]
        if len(filtered) >= 5:
            all_news = filtered
        else:
            # 放宽过滤
            relaxed = [item for item in all_news
                       if item.get("topic", "") in selected or item.get("topic", "") == "其他"]
            if len(relaxed) >= 3:
                all_news = relaxed

    all_news = all_news[:batch]

    # 并发生成口语化播报文本
    if all_news:
        all_news = await enrich_with_read_aloud(all_news)

    # 确保每条都有 category 字段（兼容旧前端）
    for item in all_news:
        if not item.get("category"):
            item["category"] = f"{item.get('topic', '综合')} · {item.get('source', '快讯')}"
        if not item.get("publishedAt"):
            item["publishedAt"] = "刚刚"
        if not item.get("sourceUrl"):
            item["sourceUrl"] = item.get("url", "#")
        if "url" in item:
            item["sourceUrl"] = item["sourceUrl"] or item["url"]
        if not isinstance(item.get("detail"), dict) or not item.get("detail"):
            item["detail"] = build_fallback_detail(item)

    result["news"] = all_news
    result["cached"] = False
    write_news_snapshot(selected + selected_sources, batch, result)
    return result


@router.get("/{news_id}")
async def get_news_item(news_id: str):
    """获取单条新闻（暂不支持，提示使用列表接口）"""
    return {"detail": "Use GET /api/news to fetch all items"}
