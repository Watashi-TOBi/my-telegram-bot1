import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN")
AI_API_KEY = os.environ.get("AI_API_KEY")

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN environment variable is not set")
if not AI_API_KEY:
    raise RuntimeError("AI_API_KEY environment variable is not set")

SUPPORT_URL = os.environ.get("SUPPORT_URL", "https://t.me/bored_hub")
OWNER_URL   = os.environ.get("OWNER_URL",   "https://t.me/Yours_Rasm")
SOURCE_URL  = os.environ.get("SOURCE_URL",  "https://github.com/")
