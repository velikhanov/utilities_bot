import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


load_dotenv()


@dataclass
class BotConfig:
    """Bot configuration management"""
    token: str
    webhook_url: str
    google_creds: str
    sheet_name: str
    scopes: List[str]

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            token=os.getenv("BOT_TOKEN"),
            webhook_url=os.getenv("WEBHOOK_URL"),
            google_creds=os.getenv("GOOGLE_CREDS"),
            sheet_name=os.getenv("SHEET_NAME"),
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

    def validate(self) -> bool:
        """Validate that all required configuration is present"""
        required_fields = [self.token, self.webhook_url, self.google_creds, self.sheet_name]
        return all(field for field in required_fields)
