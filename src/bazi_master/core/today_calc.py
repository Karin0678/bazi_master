"""
当日干支计算
计算流年、流月、流日的天干地支及五行属性，以及当前大运查询
"""

from datetime import datetime

from .bazi_calc import get_day_ganzhi, get_month_ganzhi, get_year_ganzhi_accurate
from .constants import DIZHI_WUXING, TIANGAN_WUXING


def get_today_pillars() -> dict:
    """
    计算今日的流年、流月、流日干支信息
    返回结构：
    {
        "date": {"year": int, "month": int, "day": int},
        "year":  {"tg": str, "dz": str, "gz": str, "tg_wx": str, "dz_wx": str},
        "month": {...},
        "day":   {...},
    }
    """
    now = datetime.now()
    y, m, d, h = now.year, now.month, now.day, now.hour

    year_tg, year_dz = get_year_ganzhi_accurate(y, m, d, h, 0)
    month_tg, month_dz = get_month_ganzhi(y, m, d, h, 0, year_tg)
    day_tg, day_dz = get_day_ganzhi(y, m, d, h)

    def _pillar(tg: str, dz: str) -> dict:
        return {
            "tg": tg,
            "dz": dz,
            "gz": tg + dz,
            "tg_wx": TIANGAN_WUXING[tg],
            "dz_wx": DIZHI_WUXING[dz],
        }

    return {
        "date": {"year": y, "month": m, "day": d},
        "year": _pillar(year_tg, year_dz),
        "month": _pillar(month_tg, month_dz),
        "day": _pillar(day_tg, day_dz),
    }


def get_current_dayun(dayun_data: dict, birth_year: int) -> dict | None:
    """
    返回当前所处的大运，未起运则返回 None
    """
    current_age = datetime.now().year - birth_year
    for dun in dayun_data["dayuns"]:
        if dun["age_start"] <= current_age <= dun["age_end"]:
            return dun
    return None
