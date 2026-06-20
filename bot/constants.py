import os
import json
from enum import Enum
from dataclasses import dataclass

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- Spreadsheet Structure Constants ---
COL_TYPE = "type"
COL_AMOUNT = "amount"
COL_TOTAL = "total"
COL_DESCRIPTION = "description"
COL_CREATED_AT = "created_at"

HEADERS = [COL_TYPE, COL_AMOUNT, COL_TOTAL, COL_DESCRIPTION, COL_CREATED_AT]

COL_LETTER_AMOUNT = "B"  # Column 2
COL_LETTER_TOTAL = "C"   # Column 3

NEW_SHEET_ROWS = "1000"
NEW_SHEET_COLS = "10"
# ----------------------------------------


@dataclass
class User:

    username: str
    role: str


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"


class UserRole(Enum):
    EDITOR = "editor"
    READER = "reader"


# User management (loaded dynamically from environment variable JSON string)
def get_allowed_users() -> dict[int, User]:
    raw_users = os.getenv("ALLOWED_USERS", "{}")
    try:
        data = json.loads(raw_users)
        return {
            int(user_id): User(username=info["username"], role=info["role"]) 
            for user_id, info in data.items()
        }
    except Exception as e:
        print(f"Error parsing ALLOWED_USERS env variable: {e}")
        return {}


def has_access(user_id: int) -> bool:
    return user_id in get_allowed_users()


def is_editor(user_id: int) -> bool:
    users = get_allowed_users()
    return user_id in users and users[user_id].role == UserRole.EDITOR.value


# Keyboard factory
class KeyboardFactory:
    @staticmethod
    def create_role_keyboard(role: str) -> InlineKeyboardMarkup:
        if role == UserRole.EDITOR.value:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💰 Общая сумма", callback_data="action:total")],
                    [InlineKeyboardButton(text="💵 Добавить Приход", callback_data="action:income"),
                     InlineKeyboardButton(text="💸 Добавить Расход", callback_data="action:expense")],
                    [InlineKeyboardButton(text="📊 Статистика", callback_data="action:stats_menu")]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="💰 Общая сумма", callback_data="action:total")]
                ]
            )

    @staticmethod
    def create_transaction_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="action:cancel")]
            ]
        )

    @staticmethod
    def create_statistics_type_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="📅 Текущий месяц", callback_data="stats:current"),
                 InlineKeyboardButton(text="⏮ Прошлый месяц", callback_data="stats:previous")],
                [InlineKeyboardButton(text="✏️ Ввести свой месяц", callback_data="stats:custom")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data="action:cancel")]
            ]
        )


# Pre-built keyboards
ROLE_TO_KEYBOARD = {
    role: KeyboardFactory.create_role_keyboard(role) 
    for role in [UserRole.EDITOR.value, UserRole.READER.value]
}
TRANSACTION_IN_PROGRESS_KEYBORD = KeyboardFactory.create_transaction_keyboard()
STATISTICS_TYPE_KEYBOARD = KeyboardFactory.create_statistics_type_keyboard()

ALLOWED_COMMANDS = ["/start"]
