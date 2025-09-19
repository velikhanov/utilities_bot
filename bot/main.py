from aiogram import Bot, Dispatcher

from bot.config import BotConfig
from bot.handlers import start, cancel, total, income, expense, filter

# Load configuration
config = BotConfig.from_env()

if not config.validate():
    print("Invalid configuration! Please check your environment variables.")
    raise ValueError("Missing required configuration")

# Initialize bot and dispatcher
dp = Dispatcher()
bot = Bot(token=config.token)

# Include routers
dp.include_router(start.router)
dp.include_router(cancel.router)
dp.include_router(total.router)
dp.include_router(income.router)
dp.include_router(expense.router)
dp.include_router(filter.router)
