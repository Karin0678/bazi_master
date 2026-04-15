# 部署指南

本文档介绍如何将八字命理专家部署到线上，使任何人都能通过公网地址访问。

---

## 使用 Railway 部署

[Railway](https://railway.app) 是一个支持直接连接 GitHub 仓库的云部署平台，免费套餐每月有 $5 额度（约 500 小时），个人项目完全够用。

### 前置条件

- 已有 GitHub 账号，并 Fork 或拥有本仓库
- 已准备好 AI API 密钥（Anthropic 或 DeepSeek）

---

### 步骤一：注册 Railway

前往 [https://railway.app](https://railway.app)，点击 **Login with GitHub** 完成注册与授权。

---

### 步骤二：新建项目

1. 点击右上角 **New Project**
2. 选择 **Deploy from GitHub repo**
3. 找到并选择 `bazi_master` 仓库
4. Railway 会自动读取项目根目录的 `railway.toml`，开始构建

---

### 步骤三：配置环境变量

> API 密钥通过环境变量注入，不会写入代码仓库。

在项目页面点击 **Variables** 标签，逐一添加以下变量：

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `AI_PROVIDER` | AI 提供商 | `openai_compatible` |
| `AI_API_KEY` | API 密钥 | `sk-xxxxxxxxxxxxxxxx` |
| `AI_BASE_URL` | 接口地址（DeepSeek 填此项，Claude 留空） | `https://api.deepseek.com` |
| `AI_MODEL` | 模型名称 | `deepseek-chat` |

如果使用 Anthropic Claude，变量如下：

| 变量名 | 值 |
|--------|----|
| `AI_PROVIDER` | `anthropic` |
| `AI_API_KEY` | `sk-ant-xxxxxxxxxxxxxxxx` |
| `AI_BASE_URL` | （留空不填） |
| `AI_MODEL` | `claude-sonnet-4-6` |

---

### 步骤四：获取公网地址

部署成功后：

1. 进入项目的 **Settings** → **Networking**
2. 点击 **Generate Domain**
3. Railway 会分配一个形如 `https://bazi-master-xxx.up.railway.app` 的公网地址
4. 将该地址分享给任何人，即可直接在浏览器访问

---

### 步骤五：后续更新

每次向 GitHub `main` 分支推送代码后，Railway 会自动触发重新部署，无需手动操作。

---

## 本地运行

如果只需在本机使用，参考 [README.md](./README.md) 的快速开始部分。
