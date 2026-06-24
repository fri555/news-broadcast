"""
Ask API — AI Q&A with news context + voice chat support.
"""
import time
import uuid
import json
import logging
import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models import AskRequest, ChatMessage
from services.ai import chat_with_news, has_ai

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ask", tags=["ask"])


@router.post("")
async def ask(req: AskRequest):
    """发送问题，基于新闻上下文获取 AI 回答"""
    news_title = ""
    news_context = ""

    if req.context:
        news_title = req.context.get("title", "")
        news_context = req.context.get("summary", "")
        detail = req.context.get("detail")
        if detail:
            try:
                parsed = json.loads(detail) if isinstance(detail, str) else detail
                if isinstance(parsed, dict):
                    parts = [
                        parsed.get("one_liner", ""),
                        "关键事实：" + "；".join(parsed.get("key_facts", [])[:5]) if parsed.get("key_facts") else "",
                        "背景：" + parsed.get("background", "") if parsed.get("background") else "",
                        "影响：" + parsed.get("impact", "") if parsed.get("impact") else "",
                        "来源说明：" + parsed.get("source_notes", "") if parsed.get("source_notes") else "",
                    ]
                    news_context = "\n".join([p for p in [news_context, *parts] if p])
            except Exception:
                pass

    answer = await chat_with_news(
        question=req.message,
        news_title=news_title,
        news_context=news_context,
        history=req.history if req.history else None,
    )

    return ChatMessage(
        id=str(uuid.uuid4()),
        role="assistant",
        content=answer,
        timestamp=int(time.time() * 1000),
        context=req.context,
    )


@router.post("/stream")
async def ask_stream(req: AskRequest):
    """流式追问（SSE 格式）"""
    news_title = ""
    news_context = ""

    if req.context:
        news_title = req.context.get("title", "")
        news_context = req.context.get("summary", "")
        detail = req.context.get("detail")
        if detail:
            try:
                parsed = json.loads(detail) if isinstance(detail, str) else detail
                if isinstance(parsed, dict):
                    parts = [
                        parsed.get("one_liner", ""),
                        "关键事实：" + "；".join(parsed.get("key_facts", [])[:5]) if parsed.get("key_facts") else "",
                        "背景：" + parsed.get("background", "") if parsed.get("background") else "",
                        "影响：" + parsed.get("impact", "") if parsed.get("impact") else "",
                        "来源说明：" + parsed.get("source_notes", "") if parsed.get("source_notes") else "",
                    ]
                    news_context = "\n".join([p for p in [news_context, *parts] if p])
            except Exception:
                pass

    async def generate():
        try:
            answer = await chat_with_news(
                question=req.message,
                news_title=news_title,
                news_context=news_context,
                history=req.history if req.history else None,
            )
            # 模拟流式输出
            for i in range(0, len(answer), 5):
                chunk = answer[i:i+5]
                yield f"data: {json.dumps({'content': chunk})}\n\n"
                await asyncio.sleep(0.02)
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
