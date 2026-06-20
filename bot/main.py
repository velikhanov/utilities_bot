from aiogram import Dispatcher

from bot.handlers import start, cancel, statistics, total, income, expense, filter

# Initialize dispatcher
dp = Dispatcher()

# Include routers
dp.include_router(start.router)
dp.include_router(cancel.router)
dp.include_router(total.router)
dp.include_router(income.router)
dp.include_router(expense.router)
dp.include_router(statistics.router)
dp.include_router(filter.router)
