import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import Forbidden, BadRequest, RetryAfter, TelegramError

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    try:
        raise context.error
    except Forbidden as e:
        logger.error(f"Forbidden: {e}")
    except BadRequest as e:
        logger.error(f"BadRequest: {e}")
    except RetryAfter as e:
        logger.error(f"RetryAfter: {e}")
    except TelegramError as e:
        logger.error(f"TelegramError: {e}")
    except Exception as e:
        logger.error(f"Error handling update {update}: {e}")


def register_handlers(dp):
    dp.add_error_handler(error_handler)
