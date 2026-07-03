#!/usr/bin/env python3
import asyncio

from database import init
from aiogram import Dispatcher
from config import bot
from handlers import admin_router, user_router
from loguru import logger

# logging
logger.add(
    "logs/bot.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | \n{exception}",
    level="INFO",
    rotation="00:00",
    retention="2 days",
    diagnose=True,
    backtrace=True,
)


async def main():
    pool = None
    try:
        pool = await init.init_pool()
        if pool is None:
            logger.critical("❌ Failed to create database pool. Exiting.")
            return
        await init.init_db(pool)
        dp = Dispatcher()
        dp.include_router(user_router)
        dp.include_router(admin_router)
        await dp.start_polling(bot, pool=pool)  # type: ignore
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.critical(f"❌ Unexpected error: {e}", exc_info=True)
    finally:
        if pool:
            await init.close_db(pool)
            logger.info("🔒 Database pool closed")


if __name__ == "__main__":
    logger.info("🚀 Bot starting...")
    asyncio.run(main())
