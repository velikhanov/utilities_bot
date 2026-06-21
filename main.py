import os
import asyncio
from flask import Flask, request as flask_request
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
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


@flask_app.route("/robots.txt", methods=["GET"])
def robots_txt():
    # Disallow all bots/crawlers from scanning this private webhook server
    return "User-agent: *\nDisallow: /\n", 200, {"Content-Type": "text/plain"}


@flask_app.route("/favicon.ico", methods=["GET"])
@flask_app.route("/apple-touch-icon.png", methods=["GET"])
@flask_app.route("/apple-touch-icon-precomposed.png", methods=["GET"])
def favicon():
    # Send a clean '204 No Content' response for favicon/icon requests to avoid 404 logs
    return "", 204


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
            # Check for proxy configuration (required on PythonAnywhere Free Tier)
            proxy = os.getenv("http_proxy") or os.getenv("https_proxy")
            session = AiohttpSession(proxy=proxy) if proxy else None

            local_bot = Bot(token=config.token, session=session)
            try:
                await dp.feed_update(local_bot, update)
            finally:
                await local_bot.session.close()

        asyncio.run(process_update())
        return "OK", 200
    except Exception:
        import traceback
        traceback.print_exc()
        return "Error", 500
