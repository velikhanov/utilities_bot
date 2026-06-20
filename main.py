import asyncio
from flask import Flask, request as flask_request
from aiogram import Bot
from aiogram.types import Update

from bot.main import dp
from bot.config import BotConfig


flask_app = Flask(__name__)

# Required for PythonAnywhere WSGI configuration
application = flask_app

# Load configuration
config = BotConfig.from_env()
if not config.validate():
    print("Invalid configuration! Please check your environment variables.")
    raise ValueError("Missing required configuration")


@flask_app.route("/", methods=["GET"])
def flask_home():
    return "OK", 200


@flask_app.route("/webhook", methods=["POST"])
def flask_webhook():
    # Verify the secret token header to ensure updates come from Telegram
    secret = flask_request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != config.webhook_secret:
        return "Unauthorized", 401

    try:
        data = flask_request.get_json(force=True)
        update = Update(**data)
        
        async def process_update():
            local_bot = Bot(token=config.token)
            try:
                await dp.feed_update(local_bot, update)
            finally:
                await local_bot.session.close()

        asyncio.run(process_update())
        return "OK", 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return "Error", 500
