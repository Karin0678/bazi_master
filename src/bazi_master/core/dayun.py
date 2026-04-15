"""
大运流年计算
3天=1年算法，精确到月
"""

from datetime import datetime, timedelta
from .constants import TIANGAN, DIZHI, TIANGAN_YINYANG
from .solar_terms import get_jieqi_for_dayun, JIEQI_TO_MONTH


def calculate_dayun(bazi_data: dict) -> dict:
    """
    计算大运
    - 阳男阴女：顺行（往后推节气）
    - 阴男阳女：逆行（往前推节气）
    - 3天=1年，1天=4个月
    """
    birth = bazi_data["birth"]
    gender = bazi_data["gender"]
    day_tg = bazi_data["day_master"]["tg"]
    year_tg = bazi_data["pillars"]["year"]["tg"]

    year_yinyang = TIANGAN_YINYANG[year_tg]
    is_yang_year = (year_yinyang == "阳")

    # 顺逆判断
    if gender == "男":
        forward = is_yang_year  # 阳年男命顺行
    else:
        forward = not is_yang_year  # 阴年女命顺行

    birth_dt = datetime(
        birth["year"], birth["month"], birth["day"],
        birth["hour"], birth["minute"]
    )

    # 获取节气列表
    all_terms = get_jieqi_for_dayun(birth_dt, forward)

    # 找到最近的节气（用于计算起运时间）
    if forward:
        # 顺行：找出生日之后的第一个节气
        next_term = None
        for term_dt, term_name in all_terms:
            if term_dt > birth_dt:
                next_term = (term_dt, term_name)
                break
        if next_term:
            days_diff = (next_term[0] - birth_dt).total_seconds() / 86400
        else:
            days_diff = 90  # 默认3个月
    else:
        # 逆行：找出生日之前的第一个节气
        prev_term = None
        for term_dt, term_name in reversed(all_terms):
            if term_dt < birth_dt:
                prev_term = (term_dt, term_name)
                break
        if prev_term:
            days_diff = (birth_dt - prev_term[0]).total_seconds() / 86400
        else:
            days_diff = 90

    # 3天=1年，1天=4个月
    years_to_dayun = days_diff / 3
    months_offset = int(years_to_dayun * 12)
    start_years = int(years_to_dayun)
    start_months = int((years_to_dayun - start_years) * 12)

    # 起运时间
    dayun_start_year = birth["year"] + start_years
    dayun_start_month = birth["month"] + start_months
    while dayun_start_month > 12:
        dayun_start_month -= 12
        dayun_start_year += 1

    # 计算月柱序号（用于推算大运干支）
    month_gz = bazi_data["pillars"]["month"]
    month_tg = month_gz["tg"]
    month_dz = month_gz["dz"]

    month_tg_idx = TIANGAN.index(month_tg)
    month_dz_idx = DIZHI.index(month_dz)

    # 生成10个大运
    dayuns = []
    for i in range(1, 11):
        if forward:
            offset = i
        else:
            offset = -i

        tg_idx = (month_tg_idx + offset) % 10
        dz_idx = (month_dz_idx + offset) % 12

        dayun_tg = TIANGAN[tg_idx]
        dayun_dz = DIZHI[dz_idx]

        # 大运起始年龄
        age_start = start_years + (i - 1) * 10
        age_end = age_start + 9

        # 对应公历年份
        year_start = birth["year"] + age_start
        year_end = birth["year"] + age_end

        dayuns.append({
            "index": i,
            "tg": dayun_tg,
            "dz": dayun_dz,
            "gz": dayun_tg + dayun_dz,
            "age_start": age_start,
            "age_end": age_end,
            "year_start": year_start,
            "year_end": year_end,
        })

    # 流年（当前年份前后各5年）
    current_year = datetime.now().year
    liunian = []
    for y in range(current_year - 5, current_year + 15):
        tg_idx = (y - 4) % 10
        dz_idx = (y - 4) % 12
        age = y - birth["year"]
        liunian.append({
            "year": y,
            "tg": TIANGAN[tg_idx],
            "dz": DIZHI[dz_idx],
            "gz": TIANGAN[tg_idx] + DIZHI[dz_idx],
            "age": age,
            "is_current": y == current_year,
        })

    return {
        "forward": forward,
        "direction": "顺行" if forward else "逆行",
        "days_to_dayun": round(days_diff, 1),
        "years_to_dayun": round(years_to_dayun, 1),
        "start_age": f"{start_years}岁{start_months}个月",
        "start_year": dayun_start_year,
        "start_month": dayun_start_month,
        "dayuns": dayuns,
        "liunian": liunian,
    }
