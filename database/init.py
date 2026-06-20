import asyncio
import asyncpg
from asyncpg import Pool, PostgresError
from loguru import logger
from config import QUERIES, DB_HOST, DB_NAME, DB_PASS, DB_USER, ADMIN_ID


async def init_pool() -> Pool | None:
        pool =  await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        host=DB_HOST
    )
        logger.info("Success create db pool")
        return pool


async def init_db(pool: Pool) -> None:
    try:
        async with pool.acquire() as con: #type: ignore
            async with con.transaction():
                query = QUERIES["tables"]
                logger.debug("success create query")
                await con.execute(query)
                query = """
                    UPDATE users
                    SET is_admin = True
                    WHERE chat_id = $1 ;
                    """
                await con.execute(query,ADMIN_ID)
                logger.info("success create tables")
    except PostgresError as e:
        logger.critical(f"{e}")


async def close_db(pool: Pool) -> None:
    if pool:
        await pool.close() 

