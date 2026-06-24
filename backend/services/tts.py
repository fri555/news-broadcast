"""
TTS service — Edge TTS / OpenAI TTS / MiMo TTS with file caching.
"""
import os
import re
import base64
import asyncio
import hashlib
import logging
from pathlib import Path
from typing import AsyncGenerator, Optional

import edge_tts
import httpx
from openai import AsyncOpenAI

from config import (
    TTS_PROVIDER, TTS_VOICE,
    OPENAI_TTS_API_KEY, OPENAI_TTS_BASE_URL, OPENAI_TTS_MODEL, OPENAI_TTS_VOICE,
    MIMO_TTS_API_KEY, MIMO_TTS_BASE_URL, MIMO_TTS_MODEL, MIMO_TTS_VOICE,
    has_mimo_tts,
)

logger = logging.getLogger(__name__)

AUDIO_CACHE_DIR = Path(__file__).parent.parent / "audio_cache"
AUDIO_CACHE_DIR.mkdir(exist_ok=True)


def _use_openai_tts() -> bool:
    return TTS_PROVIDER == "openai" and bool(OPENAI_TTS_API_KEY)


def _use_mimo_tts() -> bool:
    return TTS_PROVIDER == "mimo" and has_mimo_tts()


def _rate_to_speed(rate: str) -> float:
    try:
        value = int(str(rate).replace("%", "").replace("+", "").strip())
    except ValueError:
        value = 4
    return max(0.75, min(1.25, 1.0 + value / 100))


# ── MiMo TTS ─────────────────────────────────────────────

MIMO_STYLE_PROMPTS = {
    "news": "请用自然、温暖的新闻播报语气朗读，语速适中，咬字清晰，像电台新闻主播。",
    "hostA": "请用温和、专业、有亲和力的女声朗读，像在给朋友讲解新闻背景，语速稍慢。",
    "hostB": "请用活泼、轻松、有活力的男声朗读，像在和朋友聊天评论新闻，语速正常。",
    "answer": "请用简洁、耐心、友好的语气朗读，像在回答朋友的问题，语速正常。",
}


async def _mimo_tts_bytes(text: str, voice: str, rate: str = "+4%", style: str = "news") -> bytes:
    """调用 MiMo TTS API（OpenAI 兼容 chat/completions 接口），返回音频 bytes"""
    speed = _rate_to_speed(rate)
    instruction = MIMO_STYLE_PROMPTS.get(style, MIMO_STYLE_PROMPTS["news"])

    # MiMo 使用 chat/completions 接口，音频在 choices[0].message.audio.data
    payload = {
        "model": MIMO_TTS_MODEL,
        "messages": [
            {"role": "user", "content": f"语速:{speed:.1f}x。{instruction}"},
            {"role": "assistant", "content": text},
        ],
        "audio": {
            "format": "mp3",
            "voice": voice,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{MIMO_TTS_BASE_URL.rstrip('/')}/chat/completions",
                headers={
                    "api-key": MIMO_TTS_API_KEY,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            if resp.status_code != 200:
                logger.error(f"MiMo TTS error: {resp.status_code} {resp.text[:200]}")
                return b""

            data = resp.json()
            audio_b64 = data.get("choices", [{}])[0].get("message", {}).get("audio", {}).get("data", "")
            if audio_b64:
                return base64.b64decode(audio_b64)
            return b""
    except Exception as e:
        logger.error(f"MiMo TTS exception: {e}")
        return b""


# ── OpenAI TTS ───────────────────────────────────────────

def _openai_tts_instructions(style: str) -> str:
    base = "请用自然中文播客语气朗读，短句有轻微停顿，避免机械读稿。"
    if style == "hostA":
        return base + "声音温和、专业，适合解释背景。"
    if style == "hostB":
        return base + "声音轻松、有活力，适合转场和评论。"
    if style == "answer":
        return base + "像在回答朋友追问一样简洁、有耐心。"
    return base + "像新闻陪伴助手一样清晰、有节奏。"


async def _openai_tts_bytes(text: str, voice: str, rate: str = "+4%", style: str = "news") -> bytes:
    """调用 OpenAI TTS API 获取音频 bytes"""
    url = f"{OPENAI_TTS_BASE_URL.rstrip('/')}/audio/speech"
    payload = {
        "model": OPENAI_TTS_MODEL,
        "voice": voice,
        "input": text,
        "response_format": "mp3",
        "speed": _rate_to_speed(rate),
    }
    if OPENAI_TTS_MODEL == "gpt-4o-mini-tts":
        payload["instructions"] = _openai_tts_instructions(style)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {OPENAI_TTS_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if resp.status_code != 200:
            logger.error(f"OpenAI TTS error: {resp.status_code} {resp.text[:200]}")
            return b""
        return resp.content


# ── Edge TTS ─────────────────────────────────────────────

async def _edge_tts_bytes(text: str, voice: str, rate: str = "+4%", pitch: str = "+3Hz") -> bytes:
    """Edge TTS 合成到 bytes"""
    try:
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        return b"".join(chunks)
    except Exception as e:
        logger.error(f"Edge TTS error: {e}")
        return b""


# ── 统一接口 ────────────────────────────────────────────

async def tts_stream(
    text: str,
    voice: Optional[str] = None,
    rate: str = "+4%",
    pitch: str = "+3Hz",
    style: str = "news",
) -> AsyncGenerator[bytes, None]:
    """流式 TTS 合成，逐块返回音频数据"""
    v = voice or TTS_VOICE

    if _use_mimo_tts():
        v = voice or MIMO_TTS_VOICE
        audio_bytes = await _mimo_tts_bytes(text, v, rate, style)
        if audio_bytes:
            chunk_size = 4096
            for i in range(0, len(audio_bytes), chunk_size):
                yield audio_bytes[i:i + chunk_size]
                await asyncio.sleep(0.01)
        return

    if _use_openai_tts():
        v = voice if (voice and not voice.startswith("zh-CN-")) else OPENAI_TTS_VOICE
        audio_bytes = await _openai_tts_bytes(text, v, rate, style)
        if audio_bytes:
            chunk_size = 4096
            for i in range(0, len(audio_bytes), chunk_size):
                yield audio_bytes[i:i + chunk_size]
                await asyncio.sleep(0.01)
        return

    # Edge TTS 流式
    try:
        communicate = edge_tts.Communicate(text, v, rate=rate, pitch=pitch)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    except Exception as e:
        logger.error(f"Edge TTS stream error: {e}")


async def tts_to_file(
    text: str,
    voice: Optional[str] = None,
    output_path: Optional[Path] = None,
    rate: str = "+4%",
    pitch: str = "+3Hz",
    style: str = "news",
) -> bool:
    """将 TTS 合成结果保存为 MP3 文件"""
    provider = "mimo" if _use_mimo_tts() else ("openai" if _use_openai_tts() else "edge")

    if _use_mimo_tts():
        v = voice or MIMO_TTS_VOICE
    elif _use_openai_tts():
        v = voice if (voice and not voice.startswith("zh-CN-")) else OPENAI_TTS_VOICE
    else:
        v = voice or TTS_VOICE

    if not output_path:
        cache_key = hashlib.md5(f"{provider}:{v}:{rate}:{style}:{text}".encode()).hexdigest()
        output_path = AUDIO_CACHE_DIR / f"{cache_key}.mp3"

    if output_path.exists() and output_path.stat().st_size > 100:
        return True

    for attempt in range(2):
        try:
            if _use_mimo_tts():
                audio_bytes = await _mimo_tts_bytes(text, v, rate, style)
            elif _use_openai_tts():
                audio_bytes = await _openai_tts_bytes(text, v, rate, style)
            else:
                audio_bytes = await _edge_tts_bytes(text, v, rate, pitch)

            if audio_bytes:
                output_path.write_bytes(audio_bytes)
                return output_path.stat().st_size > 100
        except Exception as e:
            logger.warning(f"TTS file attempt {attempt+1} failed: {e}")
            if output_path.exists():
                output_path.unlink()

    return False
