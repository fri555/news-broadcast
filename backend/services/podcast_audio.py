"""Podcast episode building and TTS prewarm helpers."""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import MIMO_TTS_VOICE_A, MIMO_TTS_VOICE_B
from services.snapshots import read_podcast_snapshot
from services.tts import tts_cache_path, tts_to_file

logger = logging.getLogger(__name__)

PREFS_DIR = Path(__file__).parent.parent / "data" / "prefs"


def _rate_from_speed(speed: float) -> str:
    try:
        value = float(speed)
    except (TypeError, ValueError):
        value = 1.0
    percent = round((value - 1.0) * 100)
    return f"{percent:+d}%"


def _read_companion(user_id: str = "default") -> dict[str, Any]:
    defaults = {
        "voiceA": MIMO_TTS_VOICE_A,
        "voiceB": MIMO_TTS_VOICE_B,
        "speed": 1.0,
    }
    safe = (user_id or "default").replace("/", "_").replace("..", "_")
    path = PREFS_DIR / f"{safe}.json"
    if not path.exists():
        return defaults
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        companion = data.get("companion", {})
        return {**defaults, **companion}
    except Exception:
        return defaults


def known_user_ids() -> list[str]:
    ids = ["default"]
    for path in PREFS_DIR.glob("*.json"):
        if path.stem not in ids:
            ids.append(path.stem)
    return ids


def broadcast_to_podcast_episode(data: dict) -> dict:
    script = data.get("script", [])
    estimated_minutes = data.get("estimated_minutes", 10)
    chars_per_sec = 3.0

    hosts = [
        {"name": "小暖", "gender": "female", "voiceColor": "#f97316"},
        {"name": "小明", "gender": "male", "voiceColor": "#3b82f6"},
    ]

    chapters = []
    transcript = []
    elapsed = 0.0
    chapter_idx = 0

    for i, line in enumerate(script):
        text = line.get("text", "")
        line_secs = max(2, int(len(text) / chars_per_sec))
        if i == 0 or i % 5 == 0:
            chapter_idx += 1
            chapters.append({
                "id": f"ch{chapter_idx}",
                "title": f"第{chapter_idx}段 · {text[:20]}...",
                "startTime": int(elapsed),
            })
        transcript.append({
            "speaker": "小暖" if line.get("speaker") == "A" else "小明",
            "text": text,
            "startTime": int(elapsed),
            "endTime": int(elapsed + line_secs),
            "audioUrl": "",
        })
        elapsed += line_secs

    if not chapters:
        chapters.append({"id": "ch1", "title": "开场", "startTime": 0})

    return {
        "id": f"ep-{datetime.now().strftime('%Y-%m-%d-%H')}",
        "title": "NewsCast 今日新闻播报",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "duration": max(900, int(elapsed), int(estimated_minutes * 60)),
        "hosts": hosts,
        "chapters": chapters[:20],
        "transcript": transcript,
    }


def _line_audio_meta(line: dict, companion: dict) -> tuple[str, str, str]:
    is_host_a = line.get("speaker") == "小暖"
    voice = companion.get("voiceA") if is_host_a else companion.get("voiceB")
    style = "hostA" if is_host_a else "hostB"
    rate = _rate_from_speed(companion.get("speed", 1.0))
    return voice, style, rate


def attach_cached_audio_urls(episode: dict, user_id: str = "default") -> dict:
    companion = _read_companion(user_id)
    for line in episode.get("transcript", []):
        voice, style, rate = _line_audio_meta(line, companion)
        path = tts_cache_path(line.get("text", ""), voice, rate, "+3Hz", style)
        if path.exists() and path.stat().st_size > 100:
            line["audioUrl"] = f"/audio/{path.name}"
    return episode


async def prewarm_podcast_audio_for_user(user_id: str = "default") -> int:
    snapshot = read_podcast_snapshot()
    if not snapshot or not snapshot.get("script"):
        return 0

    episode = broadcast_to_podcast_episode(snapshot)
    companion = _read_companion(user_id)
    semaphore = asyncio.Semaphore(3)

    async def prewarm_line(line: dict) -> int:
        voice, style, rate = _line_audio_meta(line, companion)
        path = tts_cache_path(line.get("text", ""), voice, rate, "+3Hz", style)
        if path.exists() and path.stat().st_size > 100:
            return 0
        async with semaphore:
            try:
                ok = await asyncio.wait_for(
                    tts_to_file(line.get("text", ""), voice, path, rate, "+3Hz", style),
                    timeout=18,
                )
                return 1 if ok else 0
            except asyncio.TimeoutError:
                logger.warning("Podcast audio prewarm timed out for user %s line: %s", user_id, line.get("text", "")[:24])
                return 0

    results = await asyncio.gather(
        *(prewarm_line(line) for line in episode.get("transcript", [])),
        return_exceptions=True,
    )
    generated = sum(item for item in results if isinstance(item, int))

    logger.info("Prewarmed %s podcast audio lines for user %s", generated, user_id)
    return generated


async def prewarm_podcast_audio_for_known_users() -> None:
    for user_id in known_user_ids():
        try:
            await prewarm_podcast_audio_for_user(user_id)
            await asyncio.sleep(0.1)
        except Exception as exc:
            logger.warning("Podcast audio prewarm failed for %s: %s", user_id, exc)
