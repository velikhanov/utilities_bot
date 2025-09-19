from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.handlers.base import BaseHandler
from bot.constants import TRANSACTION_IN_PROGRESS_KEYBORD, TransactionType
from bot.db import add_transaction, get_total
from bot.states.transaction import ExpenseTransactionState


class ExpenseHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "💸 Добавить Расход")(self.start_expense)
        self.router.message(ExpenseTransactionState.waiting_for_amount)(self.process_amount)
        self.router.message(ExpenseTransactionState.waiting_for_description)(self.process_description)

    async def start_expense(self, message: Message, state: FSMContext):
        if not await self._check_editor_access(message):
            return

        if get_total() == 0:
            await message.answer("❌ Казна пуста, действие невозможно!")
            await self._show_role_keyboard(message)
            return

        await state.set_state(ExpenseTransactionState.waiting_for_amount)
        await state.update_data(transaction_type=TransactionType.EXPENSE)
        await message.answer("Введите сумму расхода:", reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD)

    async def process_amount(self, message: Message, state: FSMContext):
        try:
            amount = int(message.text.replace(",", "."))
            if amount <= 0:
                await message.answer("❌ Введите положительное число!")
                return
        except ValueError:
            await message.answer("❌ Введите корректное число!")
            return

        if get_total() < amount:
            await message.answer("❌ Сумма в казне меньше, чем введенная вами сумма. Действие невозможно!")
            await self._show_role_keyboard(message)
            return

        await state.update_data(amount=amount)
        await state.set_state(ExpenseTransactionState.waiting_for_description)
        await message.answer("Введите описание транзакции:")

    async def process_description(self, message: Message, state: FSMContext):
        data = await state.get_data()
        amount = data["amount"]
        description = message.text

        total = add_transaction(amount, data["transaction_type"], description)

        await message.answer(f"💸 Расход на сумму {amount} AZN успешно добавлен!\n✏️ Описание: {description}")
        await message.answer(f"💰 Общая сумма в казне: {total} AZN")
        await state.clear()
        await self._show_role_keyboard(message)


# Create router instance
router = ExpenseHandler().router
