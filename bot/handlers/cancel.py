from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.handlers.base import BaseHandler


class CancelHandler(BaseHandler):
    def _register_handlers(self):
        self.router.callback_query(F.data == "action:cancel")(self.cancel_transaction)

    async def cancel_transaction(self, callback: CallbackQuery, state: FSMContext):
        await state.clear()
        await self._show_role_keyboard(callback, text="Действие отменено. Выберите действие:")


# Create router instance
router = CancelHandler().router
