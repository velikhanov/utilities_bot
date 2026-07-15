from abc import ABC, abstractmethod

from aiogram import Router
from aiogram.types import Message

from bot.constants import get_allowed_users, ROLE_TO_KEYBOARD, has_access, is_editor


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
        if not has_access(message.from_user.id):
            await self._delete_message_safely(message)
            await message.answer("🚫 У вас нет доступа к этому боту!")
            return False
        return True

    async def _check_editor_access(self, message: Message) -> bool:
        """Check if user has editor role"""
        if not await self._check_user_access(message):
            return False

        if not is_editor(message.from_user.id):
            await self._delete_message_safely(message)
            await message.answer("Извините, ваш уровень доступа не позволяет совершать эту операцию!")
            await self._show_role_keyboard(message)
            return False

        return True

    async def _delete_message_safely(self, message: Message):
        """Safely delete message with error handling"""
        try:
            await message.delete()
        except Exception:
            pass

    async def _show_role_keyboard(self, message: Message, text: str = "Действие завершено. Выберите действие:"):
        """Show appropriate keyboard based on user role"""
        user_id = message.from_user.id
        users = get_allowed_users()
        if user_id not in users:
            return

        role = users[user_id].role
        keyboard = ROLE_TO_KEYBOARD[role]
        await message.answer(text, reply_markup=keyboard)

    def _get_user_role(self, message: Message) -> str:
        """Get user role"""
        users = get_allowed_users()
        if message.from_user.id in users:
            return users[message.from_user.id].role

        return "reader"

    async def _send_long_message(self, message: Message, text: str, parse_mode: str = None):
        """Send a long message by chunking it if it exceeds Telegram limits"""
        MAX_MESSAGE_LENGTH = 4000

        if len(text) <= MAX_MESSAGE_LENGTH:
            await message.answer(text, parse_mode=parse_mode)
            return

        current_chunk = ""
        for line in text.split('\n'):
            if len(current_chunk) + len(line) + 1 > MAX_MESSAGE_LENGTH:
                await message.answer(current_chunk, parse_mode=parse_mode)
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"

        if current_chunk.strip():
            await message.answer(current_chunk, parse_mode=parse_mode)
