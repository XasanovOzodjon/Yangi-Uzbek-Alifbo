import os
from pathlib import Path
from environs import Env

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env_file = BASE_DIR / ".env"
if env_file.exists():
    env.read_env(str(env_file))
else:
    env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN", default="")
ADMINS = env.list("ADMINS", default=[], subcast=int)
IP = env.str("ip", default="localhost")
DEBUG = env.bool("DEBUG", default=True)
SECRET_KEY = env.str("SECRET_KEY", default="django-insecure-alifbo-secret-key-change-in-production")
EXCEPTIONS_FILE = BASE_DIR / "data" / "exceptions.json"
