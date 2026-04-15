"""
传统规则解读引擎
基于规则字典提供八字分析文字
"""

from ..core.constants import (
    TIANGAN_WUXING, DIZHI_WUXING, TIANGAN_YINYANG,
    WUXING_SHENG, WUXING_KE, get_shishen
)


# 日主五行性格特征
DAY_MASTER_TRAITS = {
    "甲": {
        "personality": "甲木为参天大树，性格刚直不阿，有领导才能，独立自主，富有进取心。",
        "talent": "具备优秀的规划能力和远见卓识，适合从事管理、教育、法律等领域。",
        "challenge": "有时过于固执己见，需要学会灵活变通，善于倾听他人意见。",
    },
    "乙": {
        "personality": "乙木如藤蔓花草，性格温柔细腻，善于适应环境，具有坚韧的生命力。",
        "talent": "心思细腻，感受力强，适合文学艺术、设计、心理咨询等创意性工作。",
        "challenge": "有时缺乏主见，容易受外界影响，需培养独立决策的能力。",
    },
    "丙": {
        "personality": "丙火如烈日当空，性格热情开朗，慷慨大方，富有感染力，天生领袖气质。",
        "talent": "表达能力出色，善于激励他人，适合演讲、销售、公关、娱乐等行业。",
        "challenge": "情绪波动较大，需要学习自我控制，避免因冲动造成遗憾。",
    },
    "丁": {
        "personality": "丁火如灯烛之光，性格温暖体贴，内敛而深刻，有艺术气质，重情重义。",
        "talent": "直觉敏锐，洞察力强，适合艺术创作、心理分析、研究等精细工作。",
        "challenge": "内心敏感，有时过于在意他人看法，需培养自信和心理韧性。",
    },
    "戊": {
        "personality": "戊土如高山厚土，性格稳重踏实，诚实守信，有责任感，令人信赖。",
        "talent": "组织协调能力强，稳健可靠，适合行政管理、房地产、农业等领域。",
        "challenge": "有时思维偏于保守，创新意识不足，需要拓展视野，勇于尝试新事物。",
    },
    "己": {
        "personality": "己土如田园沃土，性格温和包容，善解人意，重视人际关系，内心丰富。",
        "talent": "服务意识强，善于照顾他人，适合医疗、教育、社会工作等服务性行业。",
        "challenge": "有时过于迁就他人，需要学会适时表达自己的需求和边界。",
    },
    "庚": {
        "personality": "庚金如劈金斩铁，性格刚毅果断，意志坚强，有正义感，做事干脆利落。",
        "talent": "执行力强，善于破旧立新，适合军事、法律、工程、金融等需要决断力的领域。",
        "challenge": "有时过于强硬，不善妥协，需要培养柔性沟通的技巧。",
    },
    "辛": {
        "personality": "辛金如珠宝首饰，性格精致敏感，审美品位高，追求完美，注重细节。",
        "talent": "鉴赏力强，品味独特，适合珠宝、时尚、美容、精密制造等高品质行业。",
        "challenge": "追求完美有时带来焦虑，需要学会接受不完美，放松对自己和他人的要求。",
    },
    "壬": {
        "personality": "壬水如江河湖海，性格聪明机智，思维灵活，适应力强，善于社交。",
        "talent": "智慧过人，学习能力强，适合科技、贸易、外交、咨询等需要灵活思维的领域。",
        "challenge": "有时过于随机应变，缺乏坚持，需要培养专注力和长期主义思维。",
    },
    "癸": {
        "personality": "癸水如雨露甘霖，性格细腻温柔，直觉敏锐，富有同情心，内心世界丰富。",
        "talent": "感受力强，善于捕捉微妙变化，适合文学、音乐、心理、医疗等需要细腻感知的领域。",
        "challenge": "情感丰富有时造成多虑，需要培养理性思维和情绪管理能力。",
    },
}

# 五行与方位、颜色、数字的对应
WUXING_ASSOCIATIONS = {
    "木": {"方位": "东", "颜色": "绿色、青色", "数字": "3、8", "季节": "春"},
    "火": {"方位": "南", "颜色": "红色、紫色", "数字": "2、7", "季节": "夏"},
    "土": {"方位": "中", "颜色": "黄色、棕色", "数字": "5、0", "季节": "四季"},
    "金": {"方位": "西", "颜色": "白色、金色", "数字": "4、9", "季节": "秋"},
    "水": {"方位": "北", "颜色": "黑色、蓝色", "数字": "1、6", "季节": "冬"},
}

# 五行对应行业
WUXING_CAREER = {
    "木": "教育、文化、出版、木材、绿化、农业、医疗（木系）",
    "火": "能源、娱乐、电子、餐饮、化工、灯光、文化演出",
    "土": "房地产、建筑、农业、土木工程、餐饮、仓储物流",
    "金": "金融、法律、军事、制造、珠宝、科技硬件、汽车",
    "水": "贸易、物流、旅游、传媒、咨询、网络、科技软件",
}

# 命格类型解读
MINGGE_INTERPRETATIONS = {
    "身强": {
        "overview": "日主旺盛有力，八字呈现出较为积极进取的特质。",
        "advice": "宜从事挑战性工作，善用旺盛精力创业开拓。注意避免过度自我，学会合作共赢。",
    },
    "身弱": {
        "overview": "日主较弱，需得到生扶才能发挥潜能，人生路上贵人相助尤为重要。",
        "advice": "宜选择稳定性强的工作环境，注重团队协作。保持健康作息，积累实力后再求突破。",
    },
    "中和": {
        "overview": "日主力量均衡，五行相对平和，性格较为全面，适应能力强。",
        "advice": "各方面较为均衡，可根据兴趣选择发展方向，注重持续学习和自我提升。",
    },
}


def generate_rules_analysis(bazi_data: dict, wuxing_analysis: dict, dayun_data: dict, section: str = "overview") -> str:
    """
    使用规则引擎生成八字分析文字
    section: overview（命格总论）/ personality（性格天赋）/ career（事业财运）/ dayun（大运流年）
    """
    pillars = bazi_data["pillars"]
    day_tg = bazi_data["day_master"]["tg"]
    day_wx = bazi_data["day_master"]["wuxing"]
    day_yy = bazi_data["day_master"]["yinyang"]
    gender = bazi_data["gender"]
    strength = wuxing_analysis["strength"]
    xiyong = wuxing_analysis["xiyong"]

    year_gz = pillars["year"]["gz"]
    month_gz = pillars["month"]["gz"]
    day_gz = pillars["day"]["gz"]
    hour_gz = pillars["hour"]["gz"]

    if section == "overview":
        return _gen_overview(bazi_data, wuxing_analysis, day_tg, day_wx, day_yy, gender, strength, xiyong, year_gz, month_gz, day_gz, hour_gz)
    elif section == "personality":
        return _gen_personality(day_tg, day_wx, gender, strength, xiyong)
    elif section == "career":
        return _gen_career(day_wx, gender, strength, xiyong)
    elif section == "dayun":
        return _gen_dayun(dayun_data, bazi_data, wuxing_analysis)
    else:
        return _gen_overview(bazi_data, wuxing_analysis, day_tg, day_wx, day_yy, gender, strength, xiyong, year_gz, month_gz, day_gz, hour_gz)


def _gen_overview(bazi_data, wuxing_analysis, day_tg, day_wx, day_yy, gender, strength, xiyong, year_gz, month_gz, day_gz, hour_gz) -> str:
    scores = wuxing_analysis["scores"]
    month_state = wuxing_analysis["month_state"]
    xiyong_list = xiyong["xiyong"]
    jishen_list = xiyong["jishen"]

    # 五行分布描述
    sorted_wx = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strongest_wx = sorted_wx[0][0]
    weakest_wx = sorted_wx[-1][0]

    text = f"""【命格总论】

您的八字为：{year_gz}年 · {month_gz}月 · {day_gz}日 · {hour_gz}时

以{day_gz[0]}（{day_wx}·{day_yy}）为日主，月令{bazi_data['month_zhi']}中五行处于"{month_state}"状态。{MINGGE_INTERPRETATIONS[strength]['overview']}

【五行格局】

八字五行分布：木{scores['木']:.1f}分、火{scores['火']:.1f}分、土{scores['土']:.1f}分、金{scores['金']:.1f}分、水{scores['水']:.1f}分。

五行以{strongest_wx}气最旺，{weakest_wx}气最弱{"，格局较为均衡" if abs(sorted_wx[0][1] - sorted_wx[-1][1]) < 2 else "，五行分布差异较大"}。

【喜用神与忌神】

{xiyong['description']}

喜用神（{', '.join(xiyong_list)}）代表有利于您发展的方向、颜色、方位：
{chr(10).join([f"- {wx}：方位{WUXING_ASSOCIATIONS[wx]['方位']}，颜色{WUXING_ASSOCIATIONS[wx]['颜色']}，数字{WUXING_ASSOCIATIONS[wx]['数字']}" for wx in xiyong_list if wx in WUXING_ASSOCIATIONS])}

忌神（{', '.join(jishen_list)}）代表需要规避的不利因素，在重要决策时应尽量回避。

{MINGGE_INTERPRETATIONS[strength]['advice']}"""

    return text


def _gen_personality(day_tg, day_wx, gender, strength, xiyong) -> str:
    traits = DAY_MASTER_TRAITS.get(day_tg, {})
    xiyong_list = xiyong["xiyong"]

    text = f"""【性格与天赋分析】

以{day_tg}（{day_wx}）为日主，{TIANGAN_YINYANG[day_tg]}性，命主天生具有以下特质：

【核心性格】
{traits.get('personality', '')}

【天赋才能】
{traits.get('talent', '')}

【成长功课】
{traits.get('challenge', '')}

【五行影响】
日主{day_wx}属性，与您气场最契合的方向是{WUXING_ASSOCIATIONS[day_wx]['方位']}方，有利颜色为{WUXING_ASSOCIATIONS[day_wx]['颜色']}，幸运数字含{WUXING_ASSOCIATIONS[day_wx]['数字']}。

命局{"身强" if strength == "身强" else "身弱"}，{"精力充沛，行动力强，适合担当领导角色，主动开拓事业。" if strength == "身强" else "贵人运较好，善于借力，与他人合作往往能取得更好的成果。"}

【人际关系】
{"作为" + ("阳" if TIANGAN_YINYANG[day_tg] == "阳" else "阴") + day_wx + "日主，在人际交往中" + ("较为主动积极，具有感染力，但需注意不要过于强势。" if TIANGAN_YINYANG[day_tg] == "阳" else "温和细腻，善于倾听，是朋友和家人的重要情感支柱。")}"""

    return text


def _gen_career(day_wx, gender, strength, xiyong) -> str:
    xiyong_list = xiyong["xiyong"]
    jishen_list = xiyong["jishen"]

    favorable_careers = []
    for wx in xiyong_list:
        if wx in WUXING_CAREER:
            favorable_careers.append(WUXING_CAREER[wx])

    text = f"""【事业与财运分析】

【适宜行业】
根据您的命局五行喜用，以下行业与您的能量场较为契合：

{chr(10).join([f"▶ {c}" for c in favorable_careers])}

日主本身（{day_wx}）对应行业：{WUXING_CAREER.get(day_wx, '')}

【事业发展建议】
{"身强者宜自立门户，发挥主导力，适合创业或担任高管职位。事业上宜主动出击，把握机遇。" if strength == "身强" else "身弱者宜选择有背景支撑的大平台，借助团队和资源的力量。事业上宜稳扎稳打，积累口碑。"}

【财运特点】
{"日主旺盛，财运以偏财（横财、意外之财）为主，宜把握投资机会，但需防止因过于冒进而损失。" if strength == "身强" else "日主较弱，财运以正财（稳定收入）为主，宜通过踏实工作积累财富，不宜冒险投机。"}

【人生建议】
喜用神为{', '.join(xiyong_list)}，建议：
- 居住或工作地点朝向{', '.join([WUXING_ASSOCIATIONS[wx]['方位'] for wx in xiyong_list if wx in WUXING_ASSOCIATIONS])}方为宜
- 喜用颜色：{', '.join([WUXING_ASSOCIATIONS[wx]['颜色'] for wx in xiyong_list if wx in WUXING_ASSOCIATIONS])}
- 避免过多接触忌神（{', '.join(jishen_list)}）相关的行业和环境"""

    return text


def _gen_dayun(dayun_data, bazi_data, wuxing_analysis) -> str:
    direction = dayun_data["direction"]
    start_age = dayun_data["start_age"]
    start_year = dayun_data["start_year"]
    dayuns = dayun_data["dayuns"]
    xiyong_list = wuxing_analysis["xiyong"]["xiyong"]
    jishen_list = wuxing_analysis["xiyong"]["jishen"]

    from ..core.constants import TIANGAN_WUXING, DIZHI_WUXING

    dayun_descriptions = []
    for d in dayuns[:5]:  # 只展示前5个大运
        tg_wx = TIANGAN_WUXING[d["tg"]]
        dz_wx = DIZHI_WUXING[d["dz"]]
        is_favorable = tg_wx in xiyong_list or dz_wx in xiyong_list
        quality = "▲ 吉运" if is_favorable else "▼ 需谨慎"
        dayun_descriptions.append(
            f"{d['gz']}大运（{d['year_start']}-{d['year_end']}年，{d['age_start']}-{d['age_end']}岁）{quality}"
            f"\n   {tg_wx}{dz_wx}搭配，"
            f"{'此运五行有利，事业财运可期，适合主动出击扩展。' if is_favorable else '此运五行偏忌，宜守成保守，避免大的冒险决策。'}"
        )

    text = f"""【大运流年分析】

【大运方向】
命主大运{direction}，自{start_age}（{start_year}年前后）起运。

{direction}大运意味着{"从月柱往后逐步推进，运势随时间推移展开变化。" if direction == "顺行" else "从月柱往前逐步推进，早年运势需靠自身努力奠定基础。"}

【重要大运解析】

{chr(10).join(dayun_descriptions)}

【流年运势】
每年的流年天干地支与命局原有八字形成生克关系，影响当年运势。
- 当流年五行属喜用神（{', '.join(xiyong_list)}）时，该年运势较顺，适合推进重要事项
- 当流年五行属忌神（{', '.join(jishen_list)}）时，该年需要谨慎，避免重大决策

【注意事项】
大运流年分析仅供参考，实际命运还受后天努力、环境机遇等多重因素影响。
命理学的价值在于认识自身优势与不足，借以趋吉避凶，而非宿命论。"""

    return text
