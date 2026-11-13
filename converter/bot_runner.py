import asyncio
import logging
import threading

logger = logging.getLogger(__name__)

_bot_started = False
_lock = threading.Lock()


def _bot_worker():
    try:
        from loader import application, dp
        import handlers
        from utils.set_bot_commands import set_default_commands
        from utils.notify_admins import on_startup_notify

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        handlers.register_handlers(dp)

        async def post_init(app):
            await set_default_commands(app)
            await on_startup_notify(app)

        application.post_init = post_init
        application.run_polling(stop_signals=None, close_loop=False)
    except Exception as e:
        logger.error(f"Bot error: {e}")


def start_bot_background():
    global _bot_started
    with _lock:
        if _bot_started:
            return
        _bot_started = True

        bot_thread = threading.Thread(
            target=_bot_worker,
            name="TelegramBotThread",
            daemon=True
        )
        bot_thread.start()
