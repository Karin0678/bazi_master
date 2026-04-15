import os

from dotenv import load_dotenv

load_dotenv()

# AI 提供商：anthropic 或 openai_compatible
# openai_compatible 适用于 DeepSeek、OpenAI 官方、各类代理服务
AI_PROVIDER = os.getenv("AI_PROVIDER", "anthropic")

# API 密钥
AI_API_KEY = os.getenv("AI_API_KEY", "") or os.getenv("ANTHROPIC_API_KEY", "")

# Base URL（openai_compatible 模式必填，anthropic 模式留空即可）
# 示例：DeepSeek 填 https://api.deepseek.com
#       OpenAI 官方可留空（默认 https://api.openai.com/v1）
AI_BASE_URL = os.getenv("AI_BASE_URL", "")

# 模型名称
# anthropic 示例：claude-sonnet-4-6、claude-opus-4-6
# deepseek 示例：deepseek-chat、deepseek-reasoner
AI_MODEL = os.getenv("AI_MODEL", "claude-sonnet-4-6")
