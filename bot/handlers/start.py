from aiogram import F
from aiogram.types import Message

from bot.handlers.base import BaseHandler
from bot.constants import ROLE_TO_KEYBOARD, has_access


class StartHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "/start")(self.start_handler)

    async def start_handler(self, message: Message):
        if not has_access(message.from_user.id):
            await self._delete_message_safely(message)
            await message.answer("🚫 У вас нет доступа к этому боту!")
            return

        role = self._get_user_role(message)
        await message.answer("Добро пожаловать! 👋\nВыберите действие ниже:", reply_markup=ROLE_TO_KEYBOARD[role])


# Create router instance
router = StartHandler().router
