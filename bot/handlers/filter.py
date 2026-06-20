
from aiogram.types import Message

from bot.handlers.base import BaseHandler
from bot.constants import ALLOWED_BUTTONS, ALLOWED_COMMANDS, has_access


class FilterHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message()(self.handle_allowed_messages)

    async def handle_allowed_messages(self, message: Message):
        # 1. Check user access
        if not has_access(message.from_user.id):
            await self._delete_message_safely(message)
            await message.answer("🚫 У вас нет доступа к этому боту!")
            return

        # 2. Check if the command/button is allowed
        if message.text not in ALLOWED_COMMANDS + ALLOWED_BUTTONS:
            await self._delete_message_safely(message)
            await self._show_role_keyboard(message, text="Неавторизированная команда. Используйте кнопки ниже 👇")


# Create router instance
router = FilterHandler().router
