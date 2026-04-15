"""
分析 API
POST /api/analysis
"""

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal

from ..services.analysis import get_rules_analysis, get_claude_analysis

router = APIRouter()


class AnalysisInput(BaseModel):
    bazi_data: dict
    wuxing_analysis: dict
    dayun_data: dict
    mode: Literal["rules", "claude"] = "rules"
    section: str = "overview"


@router.post("")
async def analyze(input: AnalysisInput):
    """获取分析结果"""
    if input.mode == "rules":
        # 规则引擎：直接返回文本
        text = get_rules_analysis(
            input.bazi_data,
            input.wuxing_analysis,
            input.dayun_data,
            input.section
        )
        return {"success": True, "text": text}
    else:
        # Claude 模式：SSE 流式返回
        async def generate():
            try:
                async for chunk in get_claude_analysis(
                    input.bazi_data,
                    input.wuxing_analysis,
                    input.dayun_data,
                    input.section
                ):
                    yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
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
