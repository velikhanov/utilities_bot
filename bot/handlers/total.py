from aiogram import F
from aiogram.types import Message

from bot.handlers.base import BaseHandler
from bot.db import get_total


class TotalHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "📊 Общая сумма")(self.show_total)

    async def show_total(self, message: Message):
        total = get_total()
        await message.answer(f"💰 Общая сумма в казне: {total} AZN")


# Create router instance
router = TotalHandler().router
