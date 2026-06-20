import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


load_dotenv()


@dataclass
class BotConfig:
    """Bot configuration management"""
    token: str
    google_creds: str
    sheet_name: str
    scopes: List[str]
    webhook_url: str = None
    webhook_secret: str = None

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            token=os.getenv("BOT_TOKEN"),
            webhook_url=os.getenv("WEBHOOK_URL"),
            webhook_secret=os.getenv("WEBHOOK_SECRET"),
            google_creds=os.getenv("GOOGLE_CREDS"),
            sheet_name=os.getenv("SHEET_NAME"),
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
