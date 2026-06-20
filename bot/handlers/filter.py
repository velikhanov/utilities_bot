
from aiogram.types import Message, CallbackQuery

from bot.handlers.base import BaseHandler
from bot.constants import has_access, ALLOWED_COMMANDS


class FilterHandler(BaseHandler):
    def _register_handlers(self):
        self.router.message()(self.handle_unallowed_messages)
        self.router.callback_query()(self.handle_unallowed_callbacks)

    async def handle_unallowed_messages(self, message: Message):
        if not has_access(message.from_user.id):
            await self._delete_message_safely(message)
            await message.answer("🚫 У вас нет доступа к этому боту!")
            return

        if message.text in ALLOWED_COMMANDS:
            return  # Allow registered commands to pass through to their handlers

        # Delete random text messages and show/reset main menu
        await self._delete_message_safely(message)
        await self._show_role_keyboard(message, text="Пожалуйста, используйте кнопки меню 👇")

    async def handle_unallowed_callbacks(self, callback: CallbackQuery):
        if not has_access(callback.from_user.id):
            await self._delete_message_safely(callback.message)
            await callback.message.answer("🚫 У вас нет доступа к этому боту!")
            try:
                await callback.answer()
            except Exception:
                pass
            return

        try:
            await callback.answer("Эта кнопка устарела или неактивна.", show_alert=True)
        except Exception:
            pass


# Create router instance
router = FilterHandler().router
