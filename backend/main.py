import asyncio
import logging
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.news import router as news_router
from api.podcast import router as podcast_router
from api.ask import router as ask_router
from api.preferences import router as prefs_router
from api.tts import router as tts_router

from config import ENABLE_PRELOAD, PRELOAD_TIMES, PRELOAD_TZ, DEFAULT_TOPICS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NewsCast API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 路由
app.include_router(news_router)
app.include_router(podcast_router)
app.include_router(ask_router)
app.include_router(prefs_router)
app.include_router(tts_router)

# 静态文件（音频缓存目录）
AUDIO_CACHE_DIR = Path(__file__).parent / "audio_cache"
AUDIO_CACHE_DIR.mkdir(exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(AUDIO_CACHE_DIR)), name="audio")


@app.get("/api/health")
async def health():
    from config import has_ai, has_mimo_tts
    return {
        "status": "ok",
        "version": "0.2.0",
        "ai_configured": has_ai(),
        "mimo_tts_configured": has_mimo_tts(),
    }


def _parse_preload_times() -> list[dt_time]:
    """解析预加载时间配置"""
    parsed = []
    for raw in PRELOAD_TIMES.split(","):
        raw = raw.strip()
        if not raw:
            continue
        try:
            hour, minute = raw.split(":", 1)
            parsed.append(dt_time(hour=int(hour), minute=int(minute)))
        except ValueError:
            logger.warning(f"Ignoring invalid PRELOAD_TIMES value: {raw}")
    return parsed or [dt_time(6, 0), dt_time(17, 0), dt_time(21, 0)]


async def _preload_news():
    """预加载新闻到缓存（后台任务）"""
    from api.news import get_news
    from services.ai import get_or_generate_broadcast
    from services.snapshots import write_podcast_snapshot
    try:
        logger.info(f"Preloading news for topics: {DEFAULT_TOPICS}")
        result = await get_news(topics=",".join(DEFAULT_TOPICS), limit=0, refresh=True)
        news_items = result.get("news", [])
        if news_items:
            podcast_source = [
                {
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "source": item.get("source", ""),
                    "topic": item.get("topic", "") or item.get("category", ""),
                }
                for item in news_items[:10]
            ]
            podcast = await get_or_generate_broadcast(podcast_source)
            write_podcast_snapshot(podcast)
            from services.podcast_audio import prewarm_podcast_audio_for_known_users
            await prewarm_podcast_audio_for_known_users()
        logger.info(f"Preload complete: {len(news_items)} items")
    except Exception as e:
        logger.warning(f"Preload failed (non-critical): {e}")


async def _preload_scheduler():
    """定时预加载调度器"""
    preload_times = _parse_preload_times()
    tz = ZoneInfo(PRELOAD_TZ)
    logger.info(f"Preload scheduler started, times: {preload_times} @ {PRELOAD_TZ}")

    while True:
        now = datetime.now(tz)
        # 找到下一个预加载时间
        upcoming = []
        for t in preload_times:
            target = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
            if target <= now:
                target = target.replace(day=now.day + 1)  # 明天
            upcoming.append(target)
        next_run = min(upcoming)
        wait_seconds = (next_run - now).total_seconds()
        logger.info(f"Next preload at {next_run.isoformat()} ({wait_seconds:.0f}s from now)")
        await asyncio.sleep(wait_seconds)
        await _preload_news()


@app.on_event("startup")
async def startup_event():
    """启动时：立即预加载一次，然后启动定时调度"""
    if ENABLE_PRELOAD:
        # 立即预加载
        asyncio.create_task(_preload_news())
        # 启动定时调度
        asyncio.create_task(_preload_scheduler())
    else:
        logger.info("Preload disabled (ENABLE_PRELOAD=0)")
