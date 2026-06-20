from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.handlers.base import BaseHandler
from bot.constants import TRANSACTION_IN_PROGRESS_KEYBORD, TransactionType, ROLE_TO_KEYBOARD, is_editor
from bot.db import add_transaction, get_total
from bot.states.transaction import ExpenseTransactionState


class ExpenseHandler(BaseHandler):
    def _register_handlers(self):
        self.router.callback_query(F.data == "action:expense")(self.start_expense)
        self.router.message(ExpenseTransactionState.waiting_for_amount)(self.process_amount)
        self.router.message(ExpenseTransactionState.waiting_for_description)(self.process_description)

    async def start_expense(self, callback: CallbackQuery, state: FSMContext):
        if not is_editor(callback.from_user.id):
            await callback.answer("🚫 Извините, у вас нет доступа для совершения этой операции!", show_alert=True)
            return

        if get_total() == 0:
            await self._show_role_keyboard(callback, text="❌ Казна пуста, действие невозможно!")
            return

        await state.set_state(ExpenseTransactionState.waiting_for_amount)
        await state.update_data(
            transaction_type=TransactionType.EXPENSE,
            menu_message_id=callback.message.message_id
        )
        await callback.message.edit_text("Введите сумму расхода:", reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD)
        await callback.answer()

    async def process_amount(self, message: Message, state: FSMContext):
        try:
            amount = int(message.text.replace(",", "."))
            if amount <= 0:
                await message.answer("❌ Введите положительное число!")
                return
        except ValueError:
            await message.answer("❌ Введите корректное число!")
            return

        data = await state.get_data()
        menu_message_id = data.get("menu_message_id")

        if get_total() < amount:
            # Delete user message
            await self._delete_message_safely(message)
            if menu_message_id:
                role = self._get_user_role(message)
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=menu_message_id,
                    text="❌ Сумма в казне меньше, чем введенная вами сумма. Действие невозможно!",
                    reply_markup=ROLE_TO_KEYBOARD[role]
                )
            else:
                await self._show_role_keyboard(message, text="❌ Сумма в казне меньше, чем введенная вами сумма. Действие невозможно!")
            await state.clear()
            return

        await state.update_data(amount=amount)
        await state.set_state(ExpenseTransactionState.waiting_for_description)

        # Delete user message and edit original prompt to ask for description
        await self._delete_message_safely(message)
        if menu_message_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=menu_message_id,
                    text="Введите описание транзакции:",
                    reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD
                )
            except Exception:
                await message.answer("Введите описание транзакции:", reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD)
        else:
            await message.answer("Введите описание транзакции:", reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD)

    async def process_description(self, message: Message, state: FSMContext):
        data = await state.get_data()
        amount = data["amount"]
        description = message.text
        menu_message_id = data.get("menu_message_id")

        total = add_transaction(amount, data["transaction_type"], description)

        # Delete user message
        await self._delete_message_safely(message)

        text = f"💸 Расход на сумму {amount} AZN успешно добавлен!\n✏️ Описание: {description}\n💰 Общая сумма в казне: {total} AZN"
        role = self._get_user_role(message)
        keyboard = ROLE_TO_KEYBOARD[role]

        if menu_message_id:
            try:
                await message.bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=menu_message_id,
                    text=text,
                    reply_markup=keyboard
                )
            except Exception:
                await message.answer(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)

        await state.clear()


# Create router instance
router = ExpenseHandler().router
