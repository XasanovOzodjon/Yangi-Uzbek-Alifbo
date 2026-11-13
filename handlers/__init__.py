from . import users
from . import groups
from . import channels
from . import errors


def register_handlers(dp):
    users.register_handlers(dp)
    groups.register_handlers(dp)
    channels.register_handlers(dp)
    errors.register_handlers(dp)
