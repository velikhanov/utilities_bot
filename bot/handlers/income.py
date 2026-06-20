from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.handlers.base import BaseHandler
from bot.constants import TRANSACTION_IN_PROGRESS_KEYBORD, TransactionType, ROLE_TO_KEYBOARD, is_editor
from bot.db import add_transaction
from bot.states.transaction import IncomeTransactionState


class IncomeHandler(BaseHandler):
    def _register_handlers(self):
        self.router.callback_query(F.data == "action:income")(self.start_income)
        self.router.message(IncomeTransactionState.waiting_for_amount)(self.process_amount)

    async def start_income(self, callback: CallbackQuery, state: FSMContext):
        if not is_editor(callback.from_user.id):
            await callback.answer("🚫 Извините, у вас нет доступа для совершения этой операции!", show_alert=True)
            return

        await state.set_state(IncomeTransactionState.waiting_for_amount)
        await state.update_data(
            transaction_type=TransactionType.INCOME,
            menu_message_id=callback.message.message_id
        )
        await callback.message.edit_text("Введите сумму прихода:", reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD)
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

        # Add transaction
        total = add_transaction(amount, data["transaction_type"])

        # Delete user's input message to keep chat clean
        await self._delete_message_safely(message)

        text = f"💵 Приход на сумму {amount} AZN успешно добавлен!\n💰 Общая сумма в казне: {total} AZN"
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
router = IncomeHandler().router
