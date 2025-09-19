import os

from aiohttp import web
from aiogram.types import Update

from bot.main import dp, bot
from bot.config import BotConfig

# Load configuration
config = BotConfig.from_env()


async def home(request):
    return web.Response(text="Bot is running!")


async def handle(request):
    try:
        data = await request.json()
        update = Update(**data)
        await dp.feed_update(bot, update)
        return web.Response(text="OK")
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return web.Response(text="Error", status=500)


async def on_startup(app):
    try:
        await bot.set_webhook(config.webhook_url)
        print(f"Webhook set to: {config.webhook_url}")
    except Exception as e:
        print(f"Failed to set webhook: {e}")


app = web.Application()
app.router.add_get("/", home)
app.router.add_post("/webhook", handle)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting server on port {port}")
    web.run_app(app, host="0.0.0.0", port=port)
