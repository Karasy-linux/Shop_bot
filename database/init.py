import asyncpg
from asyncpg import Pool, PostgresError, InterfaceError
from config import ADMIN_ID, DB_HOST, DB_NAME, DB_PASS, DB_USER, QUERIES
from loguru import logger


async def init_pool() -> Pool | None:
    try:
        pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            host=DB_HOST,
        )
        logger.info("✅ Success create db pool")
        return pool
    except (PostgresError, ConnectionError, InterfaceError) as e:
        logger.critical(f"❌ Failed to create db pool: {e}", exc_info=True)
        return None


async def init_db(pool: Pool) -> None:
    try:
        async with pool.acquire() as con:
            async with con.transaction():
                query = QUERIES["tables"]
                logger.debug("success create query")
                await con.execute(query)
                query = """
                    UPDATE users
                    SET is_admin = True
                    WHERE chat_id = $1 ;
                    """
                await con.execute(query, ADMIN_ID)
                logger.info("✅ Success create tables")
    except PostgresError as e:
        logger.critical(f"❌ {e}", exc_info=True)


async def close_db(pool: Pool) -> None:
    if pool:
        await pool.close()
        logger.info("🔒 Database pool closed")

