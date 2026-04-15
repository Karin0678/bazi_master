"""
八字计算 API
POST /api/bazi/calculate
"""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..core.bazi_calc import calculate_bazi
from ..services.analysis import get_full_analysis_data

router = APIRouter()


class BirthInput(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="出生年份")
    month: int = Field(..., ge=1, le=12, description="出生月份")
    day: int = Field(..., ge=1, le=31, description="出生日期")
    hour: int = Field(..., ge=0, le=23, description="出生小时（24小时制）")
    minute: int = Field(0, ge=0, le=59, description="出生分钟")
    gender: str = Field("男", description="性别：男/女")
    timezone_offset: Optional[float] = Field(8.0, description="时区偏移（小时），默认东八区")


@router.post("/calculate")
async def calculate(input: BirthInput):
    """计算八字四柱、五行、大运"""
    try:
        # 时区校正（简单处理：与UTC+8的差值转为分钟）
        adjusted_hour = input.hour
        adjusted_minute = input.minute
        if input.timezone_offset is not None and input.timezone_offset != 8.0:
            offset_minutes = int((input.timezone_offset - 8.0) * 60)
            total_minutes = adjusted_hour * 60 + adjusted_minute - offset_minutes
            total_minutes = total_minutes % (24 * 60)
            adjusted_hour = total_minutes // 60
            adjusted_minute = total_minutes % 60

        bazi_data = calculate_bazi(
            input.year, input.month, input.day,
            adjusted_hour, adjusted_minute,
            input.gender
        )

        analysis_data = get_full_analysis_data(bazi_data)

        return {
            "success": True,
            "data": analysis_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
