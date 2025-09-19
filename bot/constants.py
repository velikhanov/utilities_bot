from enum import Enum
from dataclasses import dataclass
from typing import Dict

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


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


# User management
ALLOWED_USERS: Dict[int, User] = {
    1680055119: User("teymur_15", UserRole.EDITOR.value),
    1320049768: User("Ya_Anto_Nina", UserRole.EDITOR.value),
    5901547055: User("Kenan", UserRole.READER.value)
}


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
                keyboard=[[KeyboardButton(text="📊 Общая сумма")]],
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


# Pre-built keyboards
ROLE_TO_KEYBOARD = {
    role: KeyboardFactory.create_role_keyboard(role) 
    for role in [UserRole.EDITOR.value, UserRole.READER.value]
}
TRANSACTION_IN_PROGRESS_KEYBORD = KeyboardFactory.create_transaction_keyboard()
STATISTICS_TYPE_KEYBOARD = KeyboardFactory.create_statistics_type_keyboard()

# Allowed actions
ALLOWED_BUTTONS = [
    "💰 Общая сумма",
    "💵 Добавить Приход",
    "💸 Добавить Расход",
    "📊 Статистика"
    "📅 Текущий месяц",
    "⏮ Прошлый месяц",
    "✏️ Ввести месяц"
]
ALLOWED_COMMANDS = ["/start", "/clear"]
