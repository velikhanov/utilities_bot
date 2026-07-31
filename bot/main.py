from aiogram import Dispatcher

from bot.handlers import start, cancel, statistics, total, income, expense, filter
from bot.config import BotConfig
from bot.storage import SQLiteStorage

# FSM state must survive process restarts (this bot runs as a stateless Flask
# webhook), so use a file-backed store instead of the default MemoryStorage.
dp = Dispatcher(storage=SQLiteStorage(BotConfig.from_env().fsm_db_path))

# Include routers
dp.include_router(start.router)
dp.include_router(cancel.router)
dp.include_router(total.router)
dp.include_router(income.router)
dp.include_router(expense.router)
dp.include_router(statistics.router)
dp.include_router(filter.router)
