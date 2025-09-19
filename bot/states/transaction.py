from aiogram.fsm.state import State, StatesGroup


class IncomeTransactionState(StatesGroup):
    waiting_for_amount = State()


class ExpenseTransactionState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_description = State()
