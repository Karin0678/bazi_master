"""
统一分析入口，路由到规则引擎或 Claude
"""

from typing import AsyncIterator

from ..core.dayun import calculate_dayun
from ..core.wuxing import analyze_wuxing_strength
from .claude_service import stream_analysis, stream_chat
from .rules_engine import generate_rules_analysis


def get_full_analysis_data(bazi_data: dict) -> dict:
    """计算完整分析数据（五行分析 + 大运）"""
    wuxing_analysis = analyze_wuxing_strength(bazi_data)
    dayun_data = calculate_dayun(bazi_data)
    return {
        "bazi": bazi_data,
        "wuxing": wuxing_analysis,
        "dayun": dayun_data,
    }


def get_rules_analysis(bazi_data: dict, wuxing_analysis: dict, dayun_data: dict, section: str) -> str:
    """获取规则引擎分析"""
    return generate_rules_analysis(bazi_data, wuxing_analysis, dayun_data, section)


async def get_claude_analysis(bazi_data: dict, wuxing_analysis: dict, dayun_data: dict, section: str) -> AsyncIterator[str]:
    """获取 Claude 流式分析"""
    async for chunk in stream_analysis(bazi_data, wuxing_analysis, dayun_data, section):
        yield chunk


async def get_claude_chat(messages: list, bazi_data: dict, wuxing_analysis: dict, dayun_data: dict) -> AsyncIterator[str]:
    """获取 Claude 流式对话"""
    async for chunk in stream_chat(messages, bazi_data, wuxing_analysis, dayun_data):
        yield chunk
