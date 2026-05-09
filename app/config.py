from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    api_id: int = int(os.getenv("API_ID", "0"))
    api_hash: str = os.getenv("API_HASH", "")
    owner_id: int = int(os.getenv("OWNER_ID", "7363967303"))
    proxycheck_api_key: str = os.getenv("PROXYCHECK_API_KEY", "")
    db_path: str = os.getenv("DB_PATH", "data/bot.db")
    max_concurrency: int = int(os.getenv("MAX_CONCURRENCY", "500"))
    connect_timeout: int = int(os.getenv("CONNECT_TIMEOUT", "8"))
    total_timeout: int = int(os.getenv("TOTAL_TIMEOUT", "12"))
    user_cooldown_seconds: int = int(os.getenv("USER_COOLDOWN_SECONDS", "5"))
    result_ttl_hours: int = int(os.getenv("RESULT_TTL_HOURS", "24"))

settings = Settings()
