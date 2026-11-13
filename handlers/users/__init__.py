from . import start
from . import help
from . import settings
from . import echo
from . import media
from . import document


def register_handlers(dp):
    start.register_handlers(dp)
    help.register_handlers(dp)
    settings.register_handlers(dp)
    document.register_handlers(dp)
    media.register_handlers(dp)
    echo.register_handlers(dp)
