import asyncio
from flask import Flask, request as flask_request
from aiogram.types import Update

from bot.main import dp, bot
from bot.config import BotConfig


flask_app = Flask(__name__)

# Required for PythonAnywhere WSGI configuration
application = flask_app

# Load configuration
config = BotConfig.from_env()


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
        asyncio.run(dp.feed_update(bot, update))
        return "OK", 200
    except Exception:
        import traceback
        traceback.print_exc()
        return "Error", 500
