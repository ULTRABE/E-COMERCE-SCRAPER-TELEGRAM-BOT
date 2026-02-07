"""Configuration values for the Telegram bot."""

import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH if ENV_PATH.exists() else None, override=False)


def _get_int_env(name: str, default: int = 0) -> int:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = _get_int_env("OWNER_ID", 0)
CHANNEL_URL = os.getenv("CHANNEL_URL", "")
CHANNEL_BUTTON_TEXT = os.getenv("CHANNEL_BUTTON_TEXT", "🚀 Join Channel")

DATABASE_PATH = "bot_data.db"
SCRAPE_INTERVAL_SECONDS = max(30, _get_int_env("SCRAPE_INTERVAL_SECONDS", 60))
MIN_DISCOUNT = max(1, _get_int_env("MIN_DISCOUNT", 5))
MAX_DEALS_PER_RUN = max(5, _get_int_env("MAX_DEALS_PER_RUN", 40))
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
