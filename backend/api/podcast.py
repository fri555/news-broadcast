"""
Podcast / Broadcast API — AI-generated dual-host news broadcast scripts.
Replaces hardcoded demo data with real AI generation.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException

from models import BroadcastRequest
from services.ai import get_or_generate_broadcast
from services.podcast_audio import (
    attach_cached_audio_urls,
    broadcast_to_podcast_episode,
    prewarm_podcast_audio_for_user,
)
from services.snapshots import read_podcast_snapshot, write_podcast_snapshot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/podcast", tags=["podcast"])


@router.get("/latest")
async def get_latest_podcast(background_tasks: BackgroundTasks, user_id: str = "default"):
    """获取最新一期已预生成播客。"""
    snapshot = read_podcast_snapshot()
    if snapshot:
        episode = broadcast_to_podcast_episode(snapshot)
        episode = attach_cached_audio_urls(episode, user_id)
        missing_audio = any(not line.get("audioUrl") for line in episode.get("transcript", []))
        if missing_audio:
            background_tasks.add_task(prewarm_podcast_audio_for_user, user_id)
        return episode

    return {
        "id": "ep-pending",
        "title": "请先生成播客",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "duration": 0,
        "hosts": [
            {"name": "小暖", "gender": "female", "voiceColor": "#f97316"},
            {"name": "小明", "gender": "male", "voiceColor": "#3b82f6"},
        ],
        "chapters": [],
        "transcript": [],
        "message": "请访问 /api/podcast/broadcast 并提供新闻数据以生成播客",
    }


@router.post("/broadcast")
async def create_broadcast(req: BroadcastRequest, user_id: str = "default"):
    """生成双主播对话式新闻播报脚本"""
    if not req.news:
        raise HTTPException(400, "新闻列表不能为空")

    news_dicts = [item.model_dump() for item in req.news]

    try:
        data = await get_or_generate_broadcast(news_dicts)
        write_podcast_snapshot(data)
        await prewarm_podcast_audio_for_user(user_id)
    except Exception as e:
        logger.error(f"Broadcast generation failed: {e}")
        raise HTTPException(503, "播客生成失败，请稍后重试")

    return data


@router.get("/{episode_id}")
async def get_podcast(episode_id: str):
    """获取指定播客（暂不支持）"""
    return {"detail": f"Episode {episode_id} not found"}
