from aiogram.fsm.state import State, StatesGroup


class CustomMonthState(StatesGroup):
    waiting_for_month = State()
