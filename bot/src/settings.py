import os

# Slack
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET", "")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "")  # 미리 생성한 Assistant ID

# Model behavior
MODEL = os.getenv("MODEL", "gpt-4.1")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
TOP_P = float(os.getenv("TOP_P", "1.0"))

# Server
PORT = int(os.getenv("PORT", "8080"))
TZ = os.getenv("TZ", "Asia/Seoul")
