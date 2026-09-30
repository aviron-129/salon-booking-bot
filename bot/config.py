import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    token: str
    owner_id: int
    demo: bool
    db_path: str
    tz: ZoneInfo


def load_config() -> Config:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "")
    if not token:
        raise RuntimeError("BOT_TOKEN is not set (see .env.example)")
    return Config(
        token=token,
        owner_id=int(os.getenv("OWNER_ID", "0")),
        demo=os.getenv("DEMO_MODE", "1") == "1",
        db_path=os.getenv("DB_PATH", "salon.db"),
        tz=ZoneInfo(os.getenv("TIMEZONE", "Asia/Tashkent")),
    )
