import os
import json
from enum import Enum
from dataclasses import dataclass

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
    def create_role_keyboard(role: str) -> ReplyKeyboardMarkup:
        if role == UserRole.EDITOR.value:
            return ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="💰 Общая сумма")],
                    [KeyboardButton(text="💵 Добавить Приход"),
                     KeyboardButton(text="💸 Добавить Расход")],
                    [KeyboardButton(text="📊 Статистика")]
                ],
                resize_keyboard=True,
                one_time_keyboard=False
            )
        else:
            return ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="💰 Общая сумма")]],
                resize_keyboard=True,
                one_time_keyboard=False
            )

    @staticmethod
    def create_transaction_keyboard() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Отменить")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    @staticmethod
    def create_statistics_type_keyboard() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📅 Текущий месяц"),
                 KeyboardButton(text="⏮ Прошлый месяц")],
                [KeyboardButton(text="✏️ Ввести свой месяц")],
                [KeyboardButton(text="❌ Отменить")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    @staticmethod
    def create_statistics_filter_keyboard() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💸 Только Расходы"),
                 KeyboardButton(text="💵 Только Приходы")],
                [KeyboardButton(text="📋 Всё вместе")],
                [KeyboardButton(text="❌ Отменить")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )


# Pre-built keyboards
ROLE_TO_KEYBOARD = {
    role: KeyboardFactory.create_role_keyboard(role) 
    for role in [UserRole.EDITOR.value, UserRole.READER.value]
}
TRANSACTION_IN_PROGRESS_KEYBORD = KeyboardFactory.create_transaction_keyboard()
STATISTICS_TYPE_KEYBOARD = KeyboardFactory.create_statistics_type_keyboard()
STATISTICS_FILTER_KEYBOARD = KeyboardFactory.create_statistics_filter_keyboard()

ALLOWED_BUTTONS = [
    "💰 Общая сумма",
    "💵 Добавить Приход",
    "💸 Добавить Расход",
    "📊 Статистика",
    "📅 Текущий месяц",
    "⏮ Прошлый месяц",
    "✏️ Ввести свой месяц",
    "💸 Только Расходы",
    "💵 Только Приходы",
    "📋 Всё вместе",
    "❌ Отменить"
]

ALLOWED_COMMANDS = ["/start"]
