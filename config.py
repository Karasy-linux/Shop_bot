import os

from aiogram import Bot
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
TOKEN = os.getenv("TOKEN")

DB_PASS = os.getenv("DB_PASS")
DB_USER = "bot_user"
DB_NAME = "shop_bot"
DB_HOST = "127.0.0.1"
try:
    ADMIN_ID = int(os.getenv("ADMIN_ID")) #type: ignore
except ValueError as e:
    logger.critical(f"ADMIN_ID is invalid,{e}")
    os._exit(1)
if not TOKEN and not DB_PASS and not ADMIN_ID:
    logger.critical("not get the TOKEN and DB_PASS and ADMIN_ID")
    os._exit(1)

bot = Bot(TOKEN) # type: ignore

# db
DB_PATH = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}"
SQL_FILES = {
    "tables":"database/tables.sql"
}

QUERIES = {}
for query_name, path in SQL_FILES.items():
    try:
         with open(path) as f:
            QUERIES[query_name] = f.read()
    except FileNotFoundError as e:
        logger.critical(f"invalid {query_name=} {e}",exc_info=True)


