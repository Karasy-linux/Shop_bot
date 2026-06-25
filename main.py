#!/usr/bin/env python3
import asyncio

from database import init
from aiogram import Dispatcher
from config import bot
from handlers import admin_router, user_router
from loguru import logger

# loggig
logger.add(
    "logs/bot.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | \n{exception}" ,
    level="INFO",
    rotation="00:00",
    retention="2 days",
    diagnose=True,
    backtrace=True,
)

async def main():
    try:
        pool = await init.init_pool()
        await init.init_db(pool)
        dp = Dispatcher()
        dp.include_router(user_router)
        dp.include_router(admin_router)
        await dp.start_polling(bot,pool=pool) #type: ignore
    finally:
        await init.close_db(pool)
        logger.info("the database is locked")


if __name__ == "__main__":
    logger.info("bot runs")
    asyncio.run(main())

