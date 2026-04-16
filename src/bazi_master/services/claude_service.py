"""
AI 流式调用封装
支持 anthropic 和 openai_compatible（DeepSeek、OpenAI 等）两种 provider
通过 .env 中的 AI_PROVIDER 配置切换，无需改动代码
"""

from typing import AsyncIterator

from ..config import AI_API_KEY, AI_BASE_URL, AI_MODEL, AI_PROVIDER
from ..core.today_calc import get_current_dayun, get_today_pillars


def build_bazi_context(bazi_data: dict, wuxing_analysis: dict, dayun_data: dict) -> str:
    """构建八字信息上下文字符串"""
    pillars = bazi_data["pillars"]
    birth = bazi_data["birth"]

    context = f"""用户出生信息：
- 出生时间：{birth['year']}年{birth['month']}月{birth['day']}日 {birth['hour']:02d}:{birth['minute']:02d}
- 性别：{bazi_data['gender']}

八字四柱：
- 年柱：{pillars['year']['gz']}（{pillars['year']['nayin']}）十神：{pillars['year']['tg_shishen']}
- 月柱：{pillars['month']['gz']}（{pillars['month']['nayin']}）十神：{pillars['month']['tg_shishen']}
- 日柱：{pillars['day']['gz']}（{pillars['day']['nayin']}）日主
- 时柱：{pillars['hour']['gz']}（{pillars['hour']['nayin']}）十神：{pillars['hour']['tg_shishen']}

日主：{bazi_data['day_master']['tg']}（{bazi_data['day_master']['wuxing']}·{bazi_data['day_master']['yinyang']}）
月令：{bazi_data['month_zhi']}
命局强弱：{wuxing_analysis['strength']}（月令处于{wuxing_analysis['month_state']}）

五行分布（分值）：
- 木：{wuxing_analysis['scores']['木']:.1f}
- 火：{wuxing_analysis['scores']['火']:.1f}
- 土：{wuxing_analysis['scores']['土']:.1f}
- 金：{wuxing_analysis['scores']['金']:.1f}
- 水：{wuxing_analysis['scores']['水']:.1f}

喜用神：{'、'.join(wuxing_analysis['xiyong']['xiyong'])}
忌神：{'、'.join(wuxing_analysis['xiyong']['jishen'])}

大运方向：{dayun_data['direction']}
起运时间：{dayun_data['start_age']}（约{dayun_data['start_year']}年）

当前大运："""

    current_dun = get_current_dayun(dayun_data, birth["year"])
    context += f"{current_dun['gz']}（{current_dun['year_start']}-{current_dun['year_end']}年）" if current_dun else "尚未起运"

    today = get_today_pillars()
    d = today["date"]
    context += f"""

今日日期：{d['year']}年{d['month']}月{d['day']}日
流年干支：{today['year']['gz']}（天干{today['year']['tg']}·{today['year']['tg_wx']}，地支{today['year']['dz']}·{today['year']['dz_wx']}）
流月干支：{today['month']['gz']}（天干{today['month']['tg']}·{today['month']['tg_wx']}，地支{today['month']['dz']}·{today['month']['dz_wx']}）
流日干支：{today['day']['gz']}（天干{today['day']['tg']}·{today['day']['tg_wx']}，地支{today['day']['dz']}·{today['day']['dz_wx']}）"""

    return context


SECTION_PROMPTS = {
    "overview": """请根据以上八字信息，以专业八字命理师的视角，用流畅优美的文言白话混合风格，撰写一份详尽的命格总论分析。

分析要点：
1. 命格总体评价（日主五行特质、月令旺衰、格局类型）
2. 五行格局解析（各五行力量对比，是否有五行缺失）
3. 喜用神与忌神的具体含义和运用建议
4. 命局总体走向与人生主轴

要求：语言优美流畅，专业且通俗易懂，约400-600字，具有实际参考价值。""",

    "personality": """请根据以上八字信息，深入分析命主的性格特质与天赋潜能。

分析要点：
1. 日主五行性格核心特征
2. 四柱组合对性格的综合影响
3. 天赋才能与适合的发展方向
4. 人际关系模式
5. 心理特点与成长建议

要求：分析深入细腻，结合命局具体干支解读，约400-600字，对命主有实际启发意义。""",

    "career": """请根据以上八字信息，分析命主的事业财运特点和适宜方向。

分析要点：
1. 事业运势特点（官杀、财星情况）
2. 适合的行业和职业类型
3. 财运特点（正财/偏财倾向）
4. 事业发展的最佳策略
5. 需要注意的风险和挑战

要求：结合命局干支和五行喜用，给出具体实用的建议，约400-600字。""",

    "dayun": """请根据以上八字和大运信息，分析命主当前及未来的大运流年走势。

分析要点：
1. 大运整体走势概览
2. 当前大运的具体影响（机遇与挑战）
3. 未来3-5个大运的吉凶预判
4. 近几年流年重点事项
5. 把握运势的实用建议

要求：结合具体大运干支和命局喜用神，给出有价值的人生规划参考，约400-600字。""",

    "today": """请根据以上八字及今日流年、流月、流日信息，为命主解读当日运势。

分析要点：
1. 今日流年干支与命局的生克关系（今年整体运势基调）
2. 今日流月干支对本月运势的具体影响
3. 今日流日干支的当日吉凶指引
4. 结合当前大运，综合研判今日能量状态
5. 具体行动建议（适宜做的事 / 需要规避的方向）

要求：语言温和亲切，有实际参考价值，避免消极预测，注重正向引导，约400-500字。""",
}

SYSTEM_PROMPT = """你是一位精通中国传统命理学的八字命理专家，有三十年研究经验。
你精通子平真诠、滴天髓等经典命理典籍，能够从五行生克、十神配置、大运流年等多维度分析八字命局。
你的分析风格：专业严谨又通俗易懂，文字优美，富有传统文化气息，同时注重实用性和对命主的正向引导。
不要做消极预测，要帮助命主了解自身特质，趋吉避凶，积极面对人生。"""


# ── Anthropic provider ──────────────────────────────────────────────────────

async def _stream_anthropic(system: str, messages: list) -> AsyncIterator[str]:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=AI_API_KEY)
    async with client.messages.stream(
        model=AI_MODEL,
        max_tokens=1500,
        system=system,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text


# ── OpenAI-compatible provider（DeepSeek / OpenAI / 代理）────────────────────

async def _stream_openai_compatible(system: str, messages: list) -> AsyncIterator[str]:
    from openai import AsyncOpenAI
    kwargs = {"api_key": AI_API_KEY}
    if AI_BASE_URL:
        kwargs["base_url"] = AI_BASE_URL
    client = AsyncOpenAI(**kwargs)

    oai_messages = [{"role": "system", "content": system}] + messages
    stream = await client.chat.completions.create(
        model=AI_MODEL,
        messages=oai_messages,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ── 统一入口 ─────────────────────────────────────────────────────────────────

async def _stream(system: str, messages: list) -> AsyncIterator[str]:
    if not AI_API_KEY:
        yield "错误：未配置 AI_API_KEY，请在 .env 文件中设置。"
        return
    if AI_PROVIDER == "anthropic":
        async for chunk in _stream_anthropic(system, messages):
            yield chunk
    else:
        async for chunk in _stream_openai_compatible(system, messages):
            yield chunk


async def stream_analysis(bazi_data: dict, wuxing_analysis: dict, dayun_data: dict, section: str) -> AsyncIterator[str]:
    """流式生成分析文本"""
    context = build_bazi_context(bazi_data, wuxing_analysis, dayun_data)
    section_prompt = SECTION_PROMPTS.get(section, SECTION_PROMPTS["overview"])
    messages = [{"role": "user", "content": f"{context}\n\n{section_prompt}"}]
    async for chunk in _stream(SYSTEM_PROMPT, messages):
        yield chunk


async def stream_chat(messages: list, bazi_data: dict, wuxing_analysis: dict, dayun_data: dict) -> AsyncIterator[str]:
    """流式对话"""
    context = build_bazi_context(bazi_data, wuxing_analysis, dayun_data)
    system = f"""你是一位精通中国传统命理学的八字命理专家，有三十年研究经验。

命主的八字信息如下：
{context}

请基于以上命局信息，为命主提供专业的命理解答。
回答要求：
- 结合命局具体干支和五行喜用神
- 语言温和亲切，富有传统文化气息
- 给出具体实用的建议
- 不做消极预测，注重正向引导
- 如果问题与命理无关，可以礼貌地引导回到命理话题"""

    formatted = [{"role": m["role"], "content": m["content"]} for m in messages]
    async for chunk in _stream(system, formatted):
        yield chunk
