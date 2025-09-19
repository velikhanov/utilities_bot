
from aiogram.types import Message

from bot.handlers.base import BaseHandler
from bot.constants import ALLOWED_BUTTONS, ALLOWED_COMMANDS, ALLOWED_USERS


class FilterHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message()(self.handle_allowed_messages)

    async def handle_allowed_messages(self, message: Message):
        def is_allowed():
            if message.from_user.id not in ALLOWED_USERS:
                return False, "🚫 У вас нет доступа к этому боту!"

            if message.text not in ALLOWED_COMMANDS + ALLOWED_BUTTONS:
                return False, "Неавторизированная команда. Используйте кнопки ниже 👇"

            return True, None

        allowed, reply_text = is_allowed()
        if not allowed:
            await self._delete_message_safely(message)
            await message.answer(reply_text)


# Create router instance
router = FilterHandler().router
