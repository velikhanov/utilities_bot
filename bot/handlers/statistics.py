from datetime import datetime

from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.constants import STATISTICS_TYPE_KEYBOARD, STATISTICS_FILTER_KEYBOARD, BAKU_TZ
from bot.handlers.base import BaseHandler
from bot.db import get_month_stats_summary
from bot.states.statistics import StatisticsState


class StatsHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "📊 Статистика")(self.show_stats_menu)
        self.router.message(F.text == "📅 Текущий месяц")(self.stats_current)
        self.router.message(F.text == "⏮ Прошлый месяц")(self.stats_previous)
        self.router.message(F.text == "✏️ Ввести свой месяц")(self.enter_custom_month)
        self.router.message(StatisticsState.waiting_for_month)(self.process_custom_month)
        self.router.message(StatisticsState.waiting_for_filter)(self.process_filter)

    async def show_stats_menu(self, message: Message):
        if not await self._check_user_access(message):
            return

        await message.answer("Выберите месяц для статистики:", reply_markup=STATISTICS_TYPE_KEYBOARD)

    async def _ask_for_filter(self, message: Message, state: FSMContext, sheet_name: str):
        await state.update_data(sheet_name=sheet_name)
        await state.set_state(StatisticsState.waiting_for_filter)
        await message.answer("Что вы хотите увидеть?", reply_markup=STATISTICS_FILTER_KEYBOARD)

    async def stats_current(self, message: Message, state: FSMContext):
        if not await self._check_user_access(message):
            return

        now = datetime.now(BAKU_TZ)
        sheet_name = f"{now.month:02d}-{now.year}"
        await self._ask_for_filter(message, state, sheet_name)

    async def stats_previous(self, message: Message, state: FSMContext):
        if not await self._check_user_access(message):
            return

        now = datetime.now(BAKU_TZ)
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        sheet_name = f"{prev_month:02d}-{prev_year}"
        await self._ask_for_filter(message, state, sheet_name)

    async def enter_custom_month(self, message: Message, state: FSMContext):
        if not await self._check_user_access(message):
            return

        await state.set_state(StatisticsState.waiting_for_month)
        await message.answer("Введите месяц и год в формате `MM-YYYY` (например: 09-2025):")

    async def process_custom_month(self, message: Message, state: FSMContext):
        user_input = message.text.strip()
        try:
            datetime.strptime(user_input, "%m-%Y")
        except ValueError:
            await message.answer("❌ Неверный формат. Попробуйте еще раз в формате `MM-YYYY`.")
            return
        await self._ask_for_filter(message, state, user_input)

    async def process_filter(self, message: Message, state: FSMContext):
        filter_text = message.text
        if filter_text == "💸 Только Расходы":
            filter_type = "expense"
        elif filter_text == "💵 Только Приходы":
            filter_type = "income"
        elif filter_text == "📋 Всё вместе":
            filter_type = "all"
        else:
            await message.answer("❌ Выберите вариант из меню снизу 👇", reply_markup=STATISTICS_FILTER_KEYBOARD)
            return

        data = await state.get_data()
        sheet_name = data.get("sheet_name")

        stats = get_month_stats_summary(sheet_name, filter_type)
        if stats:
            await self._send_long_message(message, stats, parse_mode="Markdown")
        else:
            await message.answer(f"❌ Лист за {sheet_name} не найден.")

        await state.clear()
        await self._show_role_keyboard(message)


# Create router instance
router = StatsHandler().router
