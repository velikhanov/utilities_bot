from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.handlers.base import BaseHandler
from bot.constants import TRANSACTION_IN_PROGRESS_KEYBORD, TransactionType
from bot.db import add_transaction
from bot.states.transaction import IncomeTransactionState


class IncomeHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "💵 Добавить Приход")(self.start_income)
        self.router.message(IncomeTransactionState.waiting_for_amount)(self.process_amount)

    async def start_income(self, message: Message, state: FSMContext):
        if not await self._check_editor_access(message):
            return

        await state.set_state(IncomeTransactionState.waiting_for_amount)
        await message.answer("Введите сумму прихода:", reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD)

    async def process_amount(self, message: Message, state: FSMContext):
        amount = await self._parse_amount(message)
        if amount is None:
            return

        await state.clear()

        total = add_transaction(amount, TransactionType.INCOME)

        await message.answer(f"💵 Приход на сумму {amount} AZN успешно добавлен!")
        await message.answer(f"💰 Общая сумма в казне: {total} AZN")
        await self._show_role_keyboard(message)


# Create router instance
router = IncomeHandler().router
