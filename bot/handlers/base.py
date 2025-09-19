from abc import ABC, abstractmethod

from aiogram import Router
from aiogram.types import Message

from bot.constants import ALLOWED_USERS, ROLE_TO_KEYBOARD


class BaseHandler(ABC):
    """Base handler class with common functionality"""

    def __init__(self):
        self.router = Router()
        self._register_handlers()

    @abstractmethod
    def _register_handlers(self):
        """Register all handlers for this router"""
        pass

    async def _check_user_access(self, message: Message) -> bool:
        """Check if user has access to the bot"""
        if message.from_user.id not in ALLOWED_USERS:
            await self._delete_message_safely(message)
            await message.answer("🚫 У вас нет доступа к этому боту!")
            return False
        return True

    async def _check_editor_access(self, message: Message) -> bool:
        """Check if user has editor role"""
        if not await self._check_user_access(message):
            return False

        role = ALLOWED_USERS[message.from_user.id].role
        if role != "editor":
            await self._delete_message_safely(message)
            await message.answer("Извините, ваш уровень доступа не позволяет создавать транзакции!")
            await self._show_role_keyboard(message)
            return False
        return True

    async def _delete_message_safely(self, message: Message):
        """Safely delete message with error handling"""
        try:
            await message.delete()
        except Exception:
            pass

    async def _show_role_keyboard(self, message: Message):
        """Show appropriate keyboard based on user role"""
        role = ALLOWED_USERS[message.from_user.id].role
        await message.answer("Действие завершено. Выберите действие:", reply_markup=ROLE_TO_KEYBOARD[role])

    def _get_user_role(self, message: Message) -> str:
        """Get user role"""
        return ALLOWED_USERS[message.from_user.id].role
