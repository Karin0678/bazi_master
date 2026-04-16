# 项目记忆：bazi-master

## 项目概况
- 路径：/home/xuhairong/projects/bazi-master
- 技术栈：Python 3.12 + FastAPI + Uvicorn，前端纯 HTML/CSS/JS，无框架
- 包管理：uv，测试：pytest（uv run pytest）
- 部署：Railway，推送 main 分支自动部署

## 目录结构
```
src/bazi_master/
  core/           # 计算引擎（纯计算，不含业务）
    bazi_calc.py      # 四柱计算
    wuxing.py         # 五行旺衰 + rate_element / rate_pillar 公共评级
    dayun.py          # 大运计算
    today_calc.py     # 今日流年/流月/流日干支 + get_current_dayun
    solar_terms.py    # 节气表
    constants.py      # 天干地支常量
  services/       # 业务逻辑（调用 core，不直接被路由使用）
    rules_engine.py   # 规则引擎文本生成
    claude_service.py # AI 流式调用封装 + prompt
    analysis.py       # 统一分析入口
  api/            # HTTP 路由（薄层，只做参数校验和响应格式化）
    bazi.py / analysis.py / chat.py / router.py
  static/         # 前端静态文件
    index.html / css/style.css / js/app.js bazi.js chat.js dayun.js
```

## 编码规范（用户明确要求，必须遵守）
1. **模块职责单一**：每个文件/函数只做一件事，不混用计算、业务、展示逻辑
2. **提取公共方法**：相同逻辑只写一次，供多处调用，不允许内联重复
3. **新功能先建模块**：新功能先在 core/ 建计算模块，再在 services/ 建业务模块，最后在 api/ 暴露接口
4. **不内联**：禁止在业务函数内部直接写计算逻辑（如 datetime 查询、干支计算），必须调用 core/ 的函数

## 已有公共工具（务必复用，勿重复实现）
- `core/wuxing.py::rate_element(wx, xiyong_list, jishen_list)` → 有利/中性/不利
- `core/wuxing.py::rate_pillar(tg_wx, dz_wx, xiyong_list, jishen_list)` → 吉/平/凶
- `core/today_calc.py::get_today_pillars()` → 今日流年/流月/流日干支结构体
- `core/today_calc.py::get_current_dayun(dayun_data, birth_year)` → 当前大运 dict 或 None

## AI 模式
- 支持 anthropic 和 openai_compatible 双模式，通过 .env 的 AI_PROVIDER 切换
- 模型、API Key、Base URL 均通过环境变量配置，不硬编码

## 分析 Tab（section 名称）
overview / personality / career / dayun / today（今日运势）
