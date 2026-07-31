import os
from dataclasses import dataclass

from dotenv import load_dotenv

from bot.constants import DEFAULT_FSM_DB_PATH


load_dotenv()


@dataclass
class BotConfig:
    """Bot configuration management"""
    token: str
    google_creds: str
    sheet_name: str
    scopes: list[str]
    webhook_url: str = None
    webhook_secret: str = None
    fsm_db_path: str = None

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            token=os.getenv("BOT_TOKEN"),
            google_creds=os.getenv("GOOGLE_CREDS"),
            sheet_name=os.getenv("SHEET_NAME"),
            webhook_url=os.getenv("WEBHOOK_URL"),
            webhook_secret=os.getenv("WEBHOOK_SECRET"),
            fsm_db_path=os.getenv("FSM_DB_PATH", DEFAULT_FSM_DB_PATH),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

    def validate(self) -> bool:
        """Validate that all required configuration is present"""
        required_fields = [
            self.token,
            self.google_creds,
            self.sheet_name,
            self.webhook_url,
            self.webhook_secret
        ]
        return all(field for field in required_fields)
