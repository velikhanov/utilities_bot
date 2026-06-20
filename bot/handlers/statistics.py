from datetime import datetime
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.constants import STATISTICS_TYPE_KEYBOARD, ROLE_TO_KEYBOARD, TRANSACTION_IN_PROGRESS_KEYBORD
from bot.handlers.base import BaseHandler
from bot.db import get_expenses_stats
from bot.states.statistics import CustomMonthState


class StatsHandler(BaseHandler):
    def _register_handlers(self):
        self.router.callback_query(F.data == "action:stats_menu")(self.show_stats_menu)
        self.router.callback_query(F.data == "stats:current")(self.stats_current)
        self.router.callback_query(F.data == "stats:previous")(self.stats_previous)
        self.router.callback_query(F.data == "stats:custom")(self.enter_custom_month)
        self.router.message(CustomMonthState.waiting_for_month)(self.process_custom_month)

    async def show_stats_menu(self, callback: CallbackQuery):
        await callback.message.edit_text("Выберите месяц для статистики:", reply_markup=STATISTICS_TYPE_KEYBOARD)
        await callback.answer()

    async def stats_current(self, callback: CallbackQuery):
        now = datetime.now()
        sheet_name = f"{now.month:02d}-{now.year}"
        stats = get_expenses_stats(sheet_name)

        if not stats:
            text = f"❌ За текущий месяц ({sheet_name}) расходов не найдено."
        else:
            text = f"📊 Статистика за {sheet_name}:\n{stats}"

        await self._show_role_keyboard(callback, text=text)

    async def stats_previous(self, callback: CallbackQuery):
        now = datetime.now()
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        sheet_name = f"{prev_month:02d}-{prev_year}"

        stats = get_expenses_stats(sheet_name)
        if not stats:
            text = f"❌ Лист за {sheet_name} не найден или расходов нет."
        else:
            text = f"⏮ Статистика за {sheet_name}:\n{stats}"

        await self._show_role_keyboard(callback, text=text)

    async def enter_custom_month(self, callback: CallbackQuery, state: FSMContext):
        await state.set_state(CustomMonthState.waiting_for_month)
        await state.update_data(menu_message_id=callback.message.message_id)
        await callback.message.edit_text(
            "Введите месяц и год в формате `MM-YYYY` (например: 09-2025):",
            reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD
        )
        await callback.answer()

    async def process_custom_month(self, message: Message, state: FSMContext):
        user_input = message.text.strip()
        data = await state.get_data()
        menu_message_id = data.get("menu_message_id")

        # Delete user message to keep chat clean
        await self._delete_message_safely(message)

        try:
            datetime.strptime(user_input, "%m-%Y")
        except ValueError:
            if menu_message_id:
                try:
                    await message.bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=menu_message_id,
                        text="❌ Неверный формат. Попробуйте еще раз в формате `MM-YYYY` (например: 09-2025):",
                        reply_markup=TRANSACTION_IN_PROGRESS_KEYBORD
                    )
                except Exception:
                    pass
            return

        stats = get_expenses_stats(user_input)
        if not stats:
            text = f"❌ Лист за {user_input} не найден или расходов нет."
        else:
            text = f"✏️ Статистика за {user_input}:\n{stats}"

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
router = StatsHandler().router
