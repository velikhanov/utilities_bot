from aiogram import F
from aiogram.types import CallbackQuery

from bot.handlers.base import BaseHandler
from bot.db import get_total


class TotalHandler(BaseHandler):
    def _register_handlers(self):
        self.router.callback_query(F.data == "action:total")(self.show_total)

    async def show_total(self, callback: CallbackQuery):
        total = get_total()
        await self._show_role_keyboard(callback, text=f"💰 Общая сумма в казне: {total} AZN")


# Create router instance
router = TotalHandler().router
