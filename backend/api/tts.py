"""
TTS API — Edge TTS / OpenAI TTS / MiMo TTS 语音合成端点。
"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from models import TTSRequest
from services.tts import tts_stream, tts_to_file, _use_openai_tts, _use_mimo_tts, tts_cache_path
from config import (
    TTS_VOICE, TTS_PROVIDER,
    OPENAI_TTS_VOICE,
    MIMO_TTS_VOICE, MIMO_TTS_VOICE_A, MIMO_TTS_VOICE_B,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["tts"])

MIMO_VOICES = {"mimo_default", "冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean"}


def _resolve_voice(req: TTSRequest) -> str:
    voice = req.voice or TTS_VOICE
    if _use_mimo_tts():
        if not req.voice:
            if req.style == "hostA":
                return MIMO_TTS_VOICE_A
            if req.style == "hostB":
                return MIMO_TTS_VOICE_B
            return MIMO_TTS_VOICE
        return req.voice if req.voice in MIMO_VOICES else MIMO_TTS_VOICE
    if _use_openai_tts() and (not req.voice or req.voice.startswith("zh-CN-")):
        return OPENAI_TTS_VOICE
    return voice


@router.post("/stream")
async def tts_stream_endpoint(req: TTSRequest):
    """流式 TTS 合成（适合前端实时播放）"""
    if not req.text.strip():
        raise HTTPException(400, "文字不能为空")

    voice = _resolve_voice(req)

    async def generate():
        try:
            async for chunk in tts_stream(req.text, voice, req.rate, req.pitch, req.style):
                yield chunk
        except Exception as e:
            logger.error(f"Stream TTS error: {e}")

    return StreamingResponse(
        generate(),
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"},
    )


@router.post("")
async def tts_endpoint(req: TTSRequest):
    """TTS 合成，返回音频文件"""
    if not req.text.strip():
        raise HTTPException(400, "文字不能为空")

    voice = _resolve_voice(req)

    audio_path = tts_cache_path(req.text, voice, req.rate, req.pitch, req.style)

    if not audio_path.exists():
        ok = await tts_to_file(req.text, voice, audio_path, req.rate, req.pitch, req.style)
        if not ok:
            raise HTTPException(503, "语音合成暂时不可用，请稍后重试")

    return FileResponse(
        str(audio_path),
        media_type="audio/mpeg",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/voices")
async def get_voices():
    """返回可用的 TTS 声音列表"""
    if _use_mimo_tts():
        return {
            "provider": "mimo",
            "voices": [
                {"id": "mimo_default", "name": "MiMo 默认"},
                {"id": "冰糖", "name": "冰糖"},
                {"id": "茉莉", "name": "茉莉"},
                {"id": "苏打", "name": "苏打"},
                {"id": "白桦", "name": "白桦"},
                {"id": "Mia", "name": "Mia"},
                {"id": "Chloe", "name": "Chloe"},
                {"id": "Milo", "name": "Milo"},
                {"id": "Dean", "name": "Dean"},
            ],
            "default": MIMO_TTS_VOICE,
        }
    if _use_openai_tts():
        return {
            "provider": "openai",
            "voices": [
                {"id": "alloy", "name": "Alloy（均衡）"},
                {"id": "nova", "name": "Nova（明亮）"},
                {"id": "onyx", "name": "Onyx（沉稳）"},
                {"id": "shimmer", "name": "Shimmer（柔和）"},
                {"id": "echo", "name": "Echo（清晰）"},
            ],
            "default": OPENAI_TTS_VOICE,
        }
    return {
        "provider": "edge",
        "voices": [
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓（女声·温暖）"},
            {"id": "zh-CN-YunxiNeural", "name": "云希（男声·活泼）"},
            {"id": "zh-CN-YunjianNeural", "name": "云健（男声·沉稳）"},
            {"id": "zh-CN-XiaoyiNeural", "name": "晓伊（女声·活泼）"},
        ],
        "default": TTS_VOICE,
    }
