from asyncpg import PostgresError, Pool 
from loguru import logger


async def add_user(pool: Pool, chat_id:int, username:str) -> None:
    try:
        async with pool.acquire() as con: 
            query = """
                    INSERT INTO users(chat_id,username) VALUES($1,$2)
                    ON CONFLICT (chat_id) DO NOTHING;
                    """
            await con.execute(query, chat_id, username)
            logger.debug(f"{chat_id=},{username=}")
    except PostgresError as e:
        logger.error(f"invalid values{e}")


async def is_admin(pool: Pool, chat_id:int) -> bool: 
    if not chat_id:
        logger.warning("there is no chat_id")
        return False
    try:
        async with pool.acquire() as con: 
            query = """
                    SELECT is_admin FROM users WHERE chat_id = $1;
                    """
            res = await con.fetchval(query,chat_id)
            logger.debug(f"{chat_id=} {res=}")
            return bool(res) if res is not None else False 
    except PostgresError as e:
        logger.error(f"invalid value {chat_id=} {e}")
        return False

