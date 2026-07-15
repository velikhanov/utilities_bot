from aiogram.fsm.state import State, StatesGroup


class StatisticsState(StatesGroup):
    waiting_for_month = State()
    waiting_for_filter = State()
