from abc import ABC, abstractmethod

from aiogram import Router
from aiogram.types import Message, CallbackQuery

from bot.constants import get_allowed_users, ROLE_TO_KEYBOARD


class BaseHandler(ABC):
    """Base handler class with common functionality"""

    def __init__(self):
        self.router = Router()
        self._register_handlers()

    @abstractmethod
    def _register_handlers(self):
        """Register all handlers for this router"""
        pass

    async def _delete_message_safely(self, message: Message):
        """Safely delete message with error handling"""
        try:
            await message.delete()
        except Exception:
            pass

    async def _show_role_keyboard(self, event: Message | CallbackQuery, text: str = "Действие завершено. Выберите действие:"):
        """Show appropriate keyboard based on user role"""
        user_id = event.from_user.id
        users = get_allowed_users()
        if user_id not in users:
            return

        role = users[user_id].role
        keyboard = ROLE_TO_KEYBOARD[role]

        if isinstance(event, CallbackQuery):
            try:
                await event.message.edit_text(text, reply_markup=keyboard)
            except Exception:
                await event.message.answer(text, reply_markup=keyboard)
            try:
                await event.answer()
            except Exception:
                pass
        else:
            await event.answer(text, reply_markup=keyboard)

    def _get_user_role(self, event: Message | CallbackQuery) -> str:
        """Get user role"""
        users = get_allowed_users()
        if event.from_user.id in users:
            return users[event.from_user.id].role
        return "reader"
