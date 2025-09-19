from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.handlers.base import BaseHandler


class CancelHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "❌ Отменить")(self.cancel_transaction)

    async def cancel_transaction(self, message: Message, state: FSMContext):
        await state.clear()
        await self._show_role_keyboard(message)


# Create router instance
router = CancelHandler().router
