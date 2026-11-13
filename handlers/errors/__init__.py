from . import error_handler


def register_handlers(dp):
    error_handler.register_handlers(dp)
