import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

from telethon.sync import TelegramClient


load_dotenv()

FILE_NAME = Path('bot_parser').stem
LOG_DIR = os.path.expanduser(f'static/logs/{FILE_NAME + ".log"}')
os.makedirs(os.path.dirname(LOG_DIR), exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    filename=LOG_DIR,
    maxBytes=50000000,
    encoding='utf-8',
    backupCount=5
)

formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
PHONE = os.getenv('PHONE')
TOKEN = os.getenv('TOKEN')

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DATABASE_URL = os.getenv('DATABASE_URL')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')

SERVER_PORT = int(os.getenv('SERVER_PORT'))

SESSION_PATH = 'static/sessions/'
os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
bot_client = TelegramClient(SESSION_PATH+'bot.session', API_ID, API_HASH)

user_client = TelegramClient(
    SESSION_PATH+'client.session',
    api_id=API_ID,
    api_hash=API_HASH
)
