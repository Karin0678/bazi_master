# 八字命理专家 — Claude Code 项目指引

## 编码规范（必须遵守）

1. **模块职责单一**：`core/` 只做纯计算，`services/` 只做业务组装，`api/` 只做参数校验和响应格式化，层与层之间不跨越调用
2. **提取公共方法**：相同逻辑只写一次，多处调用；禁止在不同函数里内联重复实现同一计算
3. **新功能路径**：先在 `core/` 建计算模块 → 再在 `services/` 建业务模块 → 最后在 `api/` 暴露接口，不允许跳层
4. **禁止内联计算**：业务函数（services/）内部不直接写 datetime 操作、干支推算等逻辑，必须调用 `core/` 的函数

## 工作流

| 操作 | 命令 |
|------|------|
| 运行测试 | `uv run pytest tests/ -v` |
| 启动应用 | `uv run uvicorn bazi_master.main:app --reload` |
| 代码检查 | `uv run ruff check src/ tests/` |
| 部署 | 推送 `main` 分支，Railway 自动部署 |

> **涉及计算逻辑的改动，必须先跑测试再提交。**

## 已有公共工具（必须复用，禁止重新实现）

| 函数 | 位置 | 用途 |
|------|------|------|
| `rate_element(wx, xiyong, jishen)` | `core/wuxing.py` | 单五行评级 → 有利/中性/不利 |
| `rate_pillar(tg_wx, dz_wx, xiyong, jishen)` | `core/wuxing.py` | 柱位吉凶 → 吉/平/凶 |
| `get_today_pillars()` | `core/today_calc.py` | 今日流年/流月/流日干支结构体 |
| `get_current_dayun(dayun_data, birth_year)` | `core/today_calc.py` | 返回当前大运 dict，未起运返回 None |

## 注意事项

- `.env` 含 API 密钥，**不得提交到 Git**
- Railway 环境变量需在控制台手动配置，不从代码读取
- 节气表覆盖 1970–2030，改动 `solar_terms.py` 前先跑 `test_bazi_calc.py` 验证
- AI Provider 通过 `.env` 的 `AI_PROVIDER` 切换（anthropic / openai_compatible），不硬编码
