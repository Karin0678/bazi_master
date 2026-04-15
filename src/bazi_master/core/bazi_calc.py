"""
四柱计算模块
实现年柱、月柱、日柱、时柱的准确计算
"""

from datetime import datetime, timedelta
from .constants import (
    TIANGAN, DIZHI, TIANGAN_WUXING, DIZHI_WUXING,
    TIANGAN_YINYANG, DIZHI_YINYANG, DIZHI_CANGGAN,
    NAYIN, get_shishen, hour_to_dizhi, WUXING_SHENG, WUXING_KE
)
from .solar_terms import get_month_jieqi


def get_year_ganzhi(year: int, month: int, day: int, hour: int) -> tuple[str, str]:
    """
    计算年柱天干地支
    注意：以立春为界（若在立春前，年柱取上一年）
    """
    # 简化处理：以公历1月1日~立春前为上一年的年柱
    # 精确处理需要判断是否已过立春
    # 年份对应的天干地支
    # 甲子年为1984年
    effective_year = year
    # 粗略判断：1/1-2/3前按上一年（精确需查节气）
    # 这里在月柱计算时配合节气判断

    tg_idx = (effective_year - 4) % 10
    dz_idx = (effective_year - 4) % 12
    return TIANGAN[tg_idx], DIZHI[dz_idx]


def get_year_ganzhi_accurate(year: int, month: int, day: int, hour: int, minute: int) -> tuple[str, str]:
    """
    精确年柱计算（以立春为年界）
    """
    from .solar_terms import SOLAR_TERMS_TABLE
    lichun = SOLAR_TERMS_TABLE.get(year, {}).get("立春")
    birth_dt = datetime(year, month, day, hour, minute)

    effective_year = year
    if lichun and birth_dt < lichun:
        effective_year = year - 1

    tg_idx = (effective_year - 4) % 10
    dz_idx = (effective_year - 4) % 12
    return TIANGAN[tg_idx], DIZHI[dz_idx]


def get_month_ganzhi(year: int, month: int, day: int, hour: int, minute: int, year_tg: str) -> tuple[str, str]:
    """
    计算月柱天干地支
    月支由节气决定，月干由年干推算（五虎遁年起月法）
    """
    _, month_zhi = get_month_jieqi(year, month, day, hour, minute)

    # 五虎遁年起月法：年干决定寅月天干
    # 甲己年：寅月从丙寅起
    # 乙庚年：寅月从戊寅起
    # 丙辛年：寅月从庚寅起
    # 丁壬年：寅月从壬寅起
    # 戊癸年：寅月从甲寅起
    year_tg_to_yin_start = {
        "甲": 2, "己": 2,  # 丙寅（丙=index 2）
        "乙": 4, "庚": 4,  # 戊寅（戊=index 4）
        "丙": 6, "辛": 6,  # 庚寅（庚=index 6）
        "丁": 8, "壬": 8,  # 壬寅（壬=index 8）
        "戊": 0, "癸": 0,  # 甲寅（甲=index 0）
    }

    # 月支到月份序号（寅=1月）
    month_zhi_order = {
        "寅": 1, "卯": 2, "辰": 3, "巳": 4, "午": 5, "未": 6,
        "申": 7, "酉": 8, "戌": 9, "亥": 10, "子": 11, "丑": 12,
    }

    yin_tg_idx = year_tg_to_yin_start.get(year_tg, 0)
    month_order = month_zhi_order.get(month_zhi, 1)

    # 月干 = 寅月天干 + (月序-1)
    month_tg_idx = (yin_tg_idx + (month_order - 1)) % 10
    return TIANGAN[month_tg_idx], month_zhi


# 日柱计算：使用干支纪日
# 甲子日基准：2000年1月7日为甲子日（index=0）
DAY_GANZHI_BASE = datetime(2000, 1, 7)  # 甲子日

def get_day_ganzhi(year: int, month: int, day: int, hour: int) -> tuple[str, str]:
    """
    计算日柱天干地支
    注意：子时（23:00-01:00）属于次日
    """
    effective_day = datetime(year, month, day)
    if hour >= 23:
        effective_day += timedelta(days=1)

    delta = (effective_day - DAY_GANZHI_BASE).days
    idx = delta % 60
    tg_idx = idx % 10
    dz_idx = idx % 12
    return TIANGAN[tg_idx], DIZHI[dz_idx]


def get_hour_ganzhi(day_tg: str, hour: int) -> tuple[str, str]:
    """
    计算时柱天干地支
    时支由出生时辰决定，时干由日干推算（五鼠遁日起时法）
    """
    hour_zhi = hour_to_dizhi(hour)

    # 五鼠遁日起时法：日干决定子时天干
    day_tg_to_zi_start = {
        "甲": 0, "己": 0,  # 甲子时
        "乙": 2, "庚": 2,  # 丙子时
        "丙": 4, "辛": 4,  # 戊子时
        "丁": 6, "壬": 6,  # 庚子时
        "戊": 8, "癸": 8,  # 壬子时
    }

    # 时支序号（子=0）
    hour_zhi_order = {
        "子": 0, "丑": 1, "寅": 2, "卯": 3, "辰": 4, "巳": 5,
        "午": 6, "未": 7, "申": 8, "酉": 9, "戌": 10, "亥": 11,
    }

    zi_tg_idx = day_tg_to_zi_start.get(day_tg, 0)
    hour_order = hour_zhi_order.get(hour_zhi, 0)

    hour_tg_idx = (zi_tg_idx + hour_order) % 10
    return TIANGAN[hour_tg_idx], hour_zhi


def calculate_bazi(year: int, month: int, day: int, hour: int, minute: int = 0, gender: str = "男") -> dict:
    """
    完整八字计算
    返回四柱、五行、十神等完整信息
    """
    # 计算四柱
    year_tg, year_dz = get_year_ganzhi_accurate(year, month, day, hour, minute)
    month_tg, month_dz = get_month_ganzhi(year, month, day, hour, minute, year_tg)
    day_tg, day_dz = get_day_ganzhi(year, month, day, hour)
    hour_tg, hour_dz = get_hour_ganzhi(day_tg, hour)

    # 四柱干支字符串
    year_gz = year_tg + year_dz
    month_gz = month_tg + month_dz
    day_gz = day_tg + day_dz
    hour_gz = hour_tg + hour_dz

    # 纳音
    year_nayin = NAYIN.get(year_gz, "")
    month_nayin = NAYIN.get(month_gz, "")
    day_nayin = NAYIN.get(day_gz, "")
    hour_nayin = NAYIN.get(hour_gz, "")

    # 五行统计
    all_tg = [year_tg, month_tg, day_tg, hour_tg]
    all_dz = [year_dz, month_dz, day_dz, hour_dz]

    wuxing_count = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for tg in all_tg:
        wuxing_count[TIANGAN_WUXING[tg]] += 1
    for dz in all_dz:
        wuxing_count[DIZHI_WUXING[dz]] += 1
        # 地支藏干也计入（权重0.5）
        for cg in DIZHI_CANGGAN.get(dz, []):
            wuxing_count[TIANGAN_WUXING[cg]] += 0.5

    # 十神（以日干为主）
    def get_pillar_shishen(tg: str, dz: str) -> dict:
        tg_ss = get_shishen(day_tg, tg) if tg != day_tg else "日主"
        dz_ss_list = []
        for cg in DIZHI_CANGGAN.get(dz, []):
            ss = get_shishen(day_tg, cg)
            dz_ss_list.append(ss)
        return {
            "tg_shishen": tg_ss,
            "dz_shishen": dz_ss_list[0] if dz_ss_list else "",
        }

    year_ss = get_pillar_shishen(year_tg, year_dz)
    month_ss = get_pillar_shishen(month_tg, month_dz)
    day_ss = {"tg_shishen": "日主", "dz_shishen": get_shishen(day_tg, DIZHI_CANGGAN.get(day_dz, [""])[0]) if DIZHI_CANGGAN.get(day_dz) else ""}
    hour_ss = get_pillar_shishen(hour_tg, hour_dz)

    return {
        "pillars": {
            "year": {"tg": year_tg, "dz": year_dz, "gz": year_gz, "nayin": year_nayin, **year_ss},
            "month": {"tg": month_tg, "dz": month_dz, "gz": month_gz, "nayin": month_nayin, **month_ss},
            "day": {"tg": day_tg, "dz": day_dz, "gz": day_gz, "nayin": day_nayin, **day_ss},
            "hour": {"tg": hour_tg, "dz": hour_dz, "gz": hour_gz, "nayin": hour_nayin, **hour_ss},
        },
        "wuxing": wuxing_count,
        "day_master": {
            "tg": day_tg,
            "wuxing": TIANGAN_WUXING[day_tg],
            "yinyang": TIANGAN_YINYANG[day_tg],
        },
        "month_zhi": month_dz,
        "gender": gender,
        "birth": {
            "year": year, "month": month, "day": day,
            "hour": hour, "minute": minute,
        }
    }
