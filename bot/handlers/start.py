from aiogram import F
from aiogram.types import Message

from bot.handlers.base import BaseHandler
from bot.constants import ROLE_TO_KEYBOARD


class StartHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "/start")(self.start_handler)

    async def start_handler(self, message: Message):
        if not await self._check_user_access(message):
            return

        role = self._get_user_role(message)
        await message.answer("Добро пожаловать! 👋\nВыберите действие ниже:", reply_markup=ROLE_TO_KEYBOARD[role])


# Create router instance
router = StartHandler().router
