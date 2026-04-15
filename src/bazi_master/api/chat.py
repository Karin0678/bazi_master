"""
AI 对话 API
POST /api/chat （SSE 流式）
"""

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

from ..services.analysis import get_claude_chat
from ..core.wuxing import analyze_wuxing_strength
from ..core.dayun import calculate_dayun

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatInput(BaseModel):
    messages: List[Message]
    bazi_data: dict


@router.post("")
async def chat(input: ChatInput):
    """AI 对话（SSE 流式）"""
    wuxing_analysis = analyze_wuxing_strength(input.bazi_data)
    dayun_data = calculate_dayun(input.bazi_data)

    messages = [{"role": m.role, "content": m.content} for m in input.messages]

    async def generate():
        try:
            async for chunk in get_claude_chat(
                messages,
                input.bazi_data,
                wuxing_analysis,
                dayun_data
            ):
                yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
