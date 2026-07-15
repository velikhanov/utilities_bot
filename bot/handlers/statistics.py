from datetime import datetime, timezone, timedelta

from aiogram import F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.constants import STATISTICS_TYPE_KEYBOARD
from bot.handlers.base import BaseHandler
from bot.db import get_expenses_stats
from bot.states.statistics import CustomMonthState

BAKU_TZ = timezone(timedelta(hours=4))


class StatsHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message(F.text == "📊 Статистика")(self.show_stats_menu)
        self.router.message(F.text == "📅 Текущий месяц")(self.stats_current)
        self.router.message(F.text == "⏮ Прошлый месяц")(self.stats_previous)
        self.router.message(F.text == "✏️ Ввести свой месяц")(self.enter_custom_month)
        self.router.message(CustomMonthState.waiting_for_month)(self.process_custom_month)

    async def show_stats_menu(self, message: Message):
        if not await self._check_user_access(message):
            return

        await message.answer("Выберите месяц для статистики:", reply_markup=STATISTICS_TYPE_KEYBOARD)

    async def stats_current(self, message: Message):
        if not await self._check_user_access(message):
            return

        now = datetime.now(BAKU_TZ)
        sheet_name = f"{now.month:02d}-{now.year}"
        stats = get_expenses_stats(sheet_name)

        if not stats:
            await message.answer("❌ За текущий месяц расходов не найдено.")
        else:
            await message.answer(f"📊 Статистика за {sheet_name}:\n{stats}")

        await self._show_role_keyboard(message)

    async def stats_previous(self, message: Message):
        if not await self._check_user_access(message):
            return

        now = datetime.now(BAKU_TZ)
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        sheet_name = f"{prev_month:02d}-{prev_year}"

        stats = get_expenses_stats(sheet_name)
        if not stats:
            await message.answer(f"❌ Лист за {sheet_name} не найден или расходов нет.")
        else:
            await message.answer(f"⏮ Статистика за {sheet_name}:\n{stats}")

        await self._show_role_keyboard(message)

    async def enter_custom_month(self, message: Message, state: FSMContext):
        if not await self._check_user_access(message):
            return

        await state.set_state(CustomMonthState.waiting_for_month)
        await message.answer("Введите месяц и год в формате `MM-YYYY` (например: 09-2025):")

    async def process_custom_month(self, message: Message, state: FSMContext):
        user_input = message.text.strip()
        try:
            datetime.strptime(user_input, "%m-%Y")
        except ValueError:
            await message.answer("❌ Неверный формат. Попробуйте еще раз в формате `MM-YYYY`.")
            return

        stats = get_expenses_stats(user_input)
        if not stats:
            await message.answer(f"❌ Лист за {user_input} не найден или расходов нет.")
        else:
            await message.answer(f"✏️ Статистика за {user_input}:\n{stats}")

        await state.clear()
        await self._show_role_keyboard(message)


# Create router instance
router = StatsHandler().router
