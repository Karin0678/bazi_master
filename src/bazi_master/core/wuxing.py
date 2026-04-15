"""
五行旺衰分析与喜用神推断
"""

from .constants import (
    TIANGAN_WUXING, DIZHI_WUXING, DIZHI_CANGGAN,
    WUXING_SHENG, WUXING_KE, get_wuxing_state
)


def analyze_wuxing_strength(bazi_data: dict) -> dict:
    """
    分析五行旺衰
    返回各五行的力量值和日主强弱判断
    """
    pillars = bazi_data["pillars"]
    month_zhi = bazi_data["month_zhi"]
    day_tg = bazi_data["day_master"]["tg"]
    day_wx = bazi_data["day_master"]["wuxing"]

    # 计算各五行得分
    wuxing_score = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}

    # 天干权重：年干0.5，月干1.0，日干1.0，时干0.75
    tg_weights = [
        (pillars["year"]["tg"], 0.5),
        (pillars["month"]["tg"], 1.0),
        (pillars["day"]["tg"], 1.0),
        (pillars["hour"]["tg"], 0.75),
    ]

    # 地支权重：藏干权重
    dz_weights = [
        (pillars["year"]["dz"], 0.3),
        (pillars["month"]["dz"], 0.6),  # 月令权重最大
        (pillars["day"]["dz"], 0.3),
        (pillars["hour"]["dz"], 0.3),
    ]

    for tg, weight in tg_weights:
        wx = TIANGAN_WUXING[tg]
        # 月令加权
        state = get_wuxing_state(wx, month_zhi)
        state_multiplier = {"旺": 1.5, "相": 1.2, "休": 0.8, "囚": 0.6, "死": 0.5}
        wuxing_score[wx] += weight * state_multiplier.get(state, 1.0)

    for dz, weight in dz_weights:
        # 藏干贡献
        canggan = DIZHI_CANGGAN.get(dz, [])
        if len(canggan) == 1:
            wx = TIANGAN_WUXING[canggan[0]]
            state = get_wuxing_state(wx, month_zhi)
            state_multiplier = {"旺": 1.5, "相": 1.2, "休": 0.8, "囚": 0.6, "死": 0.5}
            wuxing_score[wx] += weight * state_multiplier.get(state, 1.0)
        elif len(canggan) >= 2:
            # 主气占60%，余气各占20%
            ratios = [0.6, 0.3, 0.1]
            for i, cg in enumerate(canggan[:3]):
                wx = TIANGAN_WUXING[cg]
                state = get_wuxing_state(wx, month_zhi)
                state_multiplier = {"旺": 1.5, "相": 1.2, "休": 0.8, "囚": 0.6, "死": 0.5}
                wuxing_score[wx] += weight * ratios[i] * state_multiplier.get(state, 1.0)

    # 判断日主强弱
    # 生我、同我的五行合计
    help_wx = set()
    help_wx.add(day_wx)  # 同我（比劫）
    # 生我
    for wx, sheng_to in WUXING_SHENG.items():
        if sheng_to == day_wx:
            help_wx.add(wx)
            break

    help_score = sum(wuxing_score[wx] for wx in help_wx)
    total_score = sum(wuxing_score.values())
    help_ratio = help_score / total_score if total_score > 0 else 0

    # 月令是否帮扶日主
    month_state = get_wuxing_state(day_wx, month_zhi)
    month_helps = month_state in ["旺", "相"]

    # 综合判断
    if help_ratio >= 0.6 or (help_ratio >= 0.45 and month_helps):
        strength = "身强"
        strength_level = "强"
    elif help_ratio >= 0.45:
        strength = "中和"
        strength_level = "中"
    else:
        strength = "身弱"
        strength_level = "弱"

    # 推断喜用神
    xiyong = determine_xiyong(day_wx, strength_level, wuxing_score)

    return {
        "scores": wuxing_score,
        "strength": strength,
        "strength_level": strength_level,
        "help_ratio": round(help_ratio, 2),
        "month_state": month_state,
        "xiyong": xiyong,
    }


def determine_xiyong(day_wx: str, strength_level: str, scores: dict) -> dict:
    """
    推断喜用神和忌神
    身强宜泄宜克，身弱宜帮宜扶
    """
    # 找出最强和最弱的五行
    sorted_wx = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_wx[0][0]
    weakest = sorted_wx[-1][0]

    if strength_level == "强":
        # 身强：用神为克我、泄我之物
        # 克我
        ke_wo = None
        for wx, ke_to in WUXING_KE.items():
            if ke_to == day_wx:
                ke_wo = wx
                break
        # 泄我（我生）
        xie_wo = WUXING_SHENG.get(day_wx)

        xiyong_wx = [ke_wo, xie_wo] if ke_wo else [xie_wo]
        jishen_wx = [day_wx]
        # 同我之物也为忌
        sheng_wo = None
        for wx, sheng_to in WUXING_SHENG.items():
            if sheng_to == day_wx:
                sheng_wo = wx
                break
        if sheng_wo:
            jishen_wx.append(sheng_wo)

    else:  # 弱或中
        # 身弱：用神为生我、同我之物
        sheng_wo = None
        for wx, sheng_to in WUXING_SHENG.items():
            if sheng_to == day_wx:
                sheng_wo = wx
                break
        xiyong_wx = [sheng_wo, day_wx] if sheng_wo else [day_wx]

        # 忌神：克我、泄我
        ke_wo = None
        for wx, ke_to in WUXING_KE.items():
            if ke_to == day_wx:
                ke_wo = wx
                break
        xie_wo = WUXING_SHENG.get(day_wx)
        jishen_wx = [wx for wx in [ke_wo, xie_wo] if wx]

    xiyong_wx = [wx for wx in xiyong_wx if wx]

    return {
        "xiyong": xiyong_wx,
        "jishen": jishen_wx,
        "description": f"日主{'身强' if strength_level == '强' else '身弱'}，喜{'、'.join(xiyong_wx)}，忌{'、'.join(jishen_wx)}"
    }
