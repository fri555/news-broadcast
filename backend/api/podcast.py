"""
Podcast / Broadcast API — AI-generated dual-host news broadcast scripts.
Replaces hardcoded demo data with real AI generation.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from models import BroadcastRequest, BroadcastResult, PodcastEpisode, PodcastHost, PodcastChapter, TranscriptLine
from services.ai import get_or_generate_broadcast, has_ai
from services.snapshots import read_podcast_snapshot, write_podcast_snapshot

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/podcast", tags=["podcast"])


def _broadcast_to_podcast_episode(data: dict) -> PodcastEpisode:
    """将广播脚本转换为兼容旧前端的 PodcastEpisode 格式"""
    script = data.get("script", [])
    total_chars = data.get("total_chars", 0)
    estimated_minutes = data.get("estimated_minutes", 10)
    chars_per_sec = 3.0  # 更接近自然播读速度，保证 15-20 分钟的体感

    # 构建 hosts
    hosts = [
        PodcastHost(name="小暖", gender="female", voiceColor="#f97316"),
        PodcastHost(name="小明", gender="male", voiceColor="#3b82f6"),
    ]

    # 构建 chapters（按脚本自然分段，简化处理）
    chapters = []
    chapter_idx = 0
    elapsed = 0
    for i, line in enumerate(script):
        line_chars = len(line["text"])
        line_secs = line_chars / chars_per_sec
        # 每 5 行或遇到新话题时创建新章节
        if i == 0 or i % 5 == 0:
            chapter_idx += 1
            chapters.append(PodcastChapter(
                id=f"ch{chapter_idx}",
                title=f"第{chapter_idx}段 · {line['text'][:20]}...",
                startTime=int(elapsed),
            ))
        elapsed += line_secs

    if not chapters:
        chapters.append(PodcastChapter(id="ch1", title="开场", startTime=0))

    # 构建 transcript
    transcript = []
    elapsed = 0
    for i, line in enumerate(script):
        line_chars = len(line["text"])
        line_secs = max(2, int(line_chars / chars_per_sec))
        speaker_name = "小暖" if line["speaker"] == "A" else "小明"
        transcript.append(TranscriptLine(
            speaker=speaker_name,
            text=line["text"],
            startTime=int(elapsed),
            endTime=int(elapsed + line_secs),
        ))
        elapsed += line_secs

    duration = max(900, int(elapsed), int(estimated_minutes * 60))

    return PodcastEpisode(
        id=f"ep-{datetime.now().strftime('%Y-%m-%d-%H')}",
        title="NewsCast 今日新闻播报",
        date=datetime.now().strftime("%Y-%m-%d"),
        duration=duration,
        hosts=hosts,
        chapters=chapters[:20],  # 限制章节数
        transcript=transcript,
    )


@router.get("/latest")
async def get_latest_podcast():
    """获取最新一期已预生成播客。"""
    snapshot = read_podcast_snapshot()
    if snapshot:
        return _broadcast_to_podcast_episode(snapshot)

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
async def create_broadcast(req: BroadcastRequest):
    """生成双主播对话式新闻播报脚本"""
    if not req.news:
        raise HTTPException(400, "新闻列表不能为空")

    news_dicts = [item.model_dump() for item in req.news]

    try:
        data = await get_or_generate_broadcast(news_dicts)
        write_podcast_snapshot(data)
    except Exception as e:
        logger.error(f"Broadcast generation failed: {e}")
        raise HTTPException(503, "播客生成失败，请稍后重试")

    return data


@router.get("/{episode_id}")
async def get_podcast(episode_id: str):
    """获取指定播客（暂不支持）"""
    return {"detail": f"Episode {episode_id} not found"}
