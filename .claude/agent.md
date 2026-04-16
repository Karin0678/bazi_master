# 八字命理专家 — 项目专属配置

## 项目信息

**技术栈**：FastAPI · Python 3.12 · uv · SSE 流式输出
**AI 配置**：通过 `.env` 切换 Provider，当前使用 DeepSeek（`openai_compatible`）
**启动命令**：`uv run uvicorn bazi_master.main:app --host 0.0.0.0 --port 8000`
**测试命令**：`uv run pytest tests/ -v`
**线上地址**：https://bazimaster-production.up.railway.app/
**代码仓库**：https://github.com/Karin0678/bazi_master

## 核心模块路径

| 模块 | 路径 |
|------|------|
| 四柱计算 | `src/bazi_master/core/bazi_calc.py` |
| 节气时间表（1970–2030） | `src/bazi_master/core/solar_terms.py` |
| AI 流式服务 | `src/bazi_master/services/claude_service.py` |
| 多 Provider 配置 | `src/bazi_master/config.py` |
| 分析 SSE 接口 | `src/bazi_master/api/analysis.py` |

## 注意事项

- `.env` 已在 `.gitignore` 中，不得提交到 Git
- 节气表覆盖 1970–2030，修改前先跑 `test_bazi_calc.py` 验证
- Railway 环境变量需在控制台手动配置，不从代码读取
