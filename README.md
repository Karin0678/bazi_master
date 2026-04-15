# 八字命理专家

一款基于中国传统命理学的八字排盘与分析 Web 应用，融合规则引擎与 AI 大模型，提供专业的四柱命理解读。

---

## 项目背景

八字命理（子平术）是中国传统文化中流传数千年的命理体系，以人出生的年、月、日、时对应的天干地支（即"四柱八字"）为核心，通过五行生克、十神配置、大运流年等维度分析人的性格特质、事业财运与人生走势。

本项目旨在将传统命理知识与现代 Web 技术结合，实现：

- **精确排盘**：基于节气时间表精确计算四柱，以立春为年界、十二节为月界，覆盖 1970–2030 年
- **规则引擎解析**：将命理典籍（子平真诠、滴天髓）中的核心规则程序化，离线即可输出分析文本
- **AI 深度解读**：接入大语言模型（支持 Anthropic Claude / DeepSeek 等），以命理专家视角生成流畅的文言白话混合风格解读，流式输出，实时呈现
- **命理问答对话**：基于命主八字信息的上下文，支持自然语言追问与交互

---

## 功能特性

| 功能 | 说明 |
|------|------|
| 四柱排盘 | 年柱、月柱、日柱、时柱，含纳音、十神 |
| 五行分析 | 五行分值统计、日主强弱判断、月令旺衰 |
| 喜用神 / 忌神 | 基于格局自动推断喜用忌神 |
| 大运排盘 | 起运年龄、大运方向、逐步大运干支 |
| 命理分析（规则引擎） | 离线模式，快速输出结构化分析 |
| AI 深度解读（流式） | 命格总论、性格特质、事业财运、大运流年四大板块 |
| AI 命理对话 | 基于命局的上下文问答，支持追问 |

---

## 技术栈

- **后端**：Python 3.12 / FastAPI / Uvicorn
- **AI 集成**：Anthropic SDK（Claude）/ OpenAI SDK（DeepSeek 及其他兼容接口）
- **流式输出**：SSE（Server-Sent Events）
- **前端**：原生 HTML / CSS / JavaScript（无框架依赖）
- **包管理**：uv
- **部署**：支持 Railway（含 `railway.toml` 配置）

---

## 项目结构

```
bazi-master/
├── src/
│   └── bazi_master/
│       ├── main.py                 # FastAPI 应用入口
│       ├── config.py               # 多 Provider AI 配置（读取 .env）
│       ├── api/
│       │   ├── router.py           # 路由注册
│       │   ├── bazi.py             # POST /api/bazi  排盘接口
│       │   ├── analysis.py         # POST /api/analysis  分析接口（SSE）
│       │   └── chat.py             # POST /api/chat  对话接口（SSE）
│       ├── core/
│       │   ├── bazi_calc.py        # 四柱计算（年/月/日/时柱）
│       │   ├── solar_terms.py      # 节气时间表（1970–2030）
│       │   ├── dayun.py            # 大运排盘
│       │   ├── wuxing.py           # 五行分析 & 喜用神
│       │   └── constants.py        # 天干地支、五行、十神常量
│       ├── services/
│       │   ├── analysis.py         # 分析服务（调度规则引擎 / AI）
│       │   ├── claude_service.py   # AI 流式调用封装（双 Provider）
│       │   └── rules_engine.py     # 规则引擎（离线文本生成）
│       └── static/
│           ├── index.html          # 单页前端
│           ├── css/style.css
│           └── js/
│               ├── app.js          # 主逻辑、页面交互
│               ├── bazi.js         # 排盘结果渲染
│               ├── chat.js         # AI 对话组件
│               └── dayun.js        # 大运时间轴渲染
├── tests/
│   ├── test_bazi_calc.py           # 四柱计算准确性测试
│   └── test_rules_engine.py        # 规则引擎单元测试
├── .env.example                    # 环境变量模板
├── .gitignore
├── pyproject.toml
├── railway.toml                    # Railway 部署配置
└── uv.lock
```

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Karin0678/bazi_master.git
cd bazi_master
```

### 2. 安装依赖

需要 Python 3.12+，推荐使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv sync
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 AI 配置：

```env
# 使用 Anthropic Claude
AI_PROVIDER=anthropic
AI_API_KEY=sk-ant-你的密钥
AI_BASE_URL=
AI_MODEL=claude-sonnet-4-6

# 或使用 DeepSeek
AI_PROVIDER=openai_compatible
AI_API_KEY=sk-你的密钥
AI_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat
```

### 4. 启动服务

```bash
uv run uvicorn bazi_master.main:app --host 0.0.0.0 --port 8000
```

浏览器访问 [http://localhost:8000](http://localhost:8000)

---

## AI Provider 配置说明

本项目支持两种 AI 提供商，通过 `.env` 文件切换，无需修改代码：

| 配置项 | Anthropic | DeepSeek / OpenAI 兼容 |
|--------|-----------|------------------------|
| `AI_PROVIDER` | `anthropic` | `openai_compatible` |
| `AI_API_KEY` | Anthropic 密钥 | 对应服务密钥 |
| `AI_BASE_URL` | 留空 | `https://api.deepseek.com` |
| `AI_MODEL` | `claude-sonnet-4-6` | `deepseek-chat` |

---

## 运行测试

```bash
uv run pytest tests/ -v
```

---

## 部署到 Railway

项目已包含 `railway.toml`，直接连接 GitHub 仓库即可一键部署。在 Railway 控制台添加环境变量（同 `.env` 内容）后自动启动。

---

## 许可证

MIT License
