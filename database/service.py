from asyncpg import Pool, PostgresError
from loguru import logger
from config import DEFUALT_IMG 

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


async def check_product_name(pool: Pool, name:str | None) -> bool:
    if not name:
        logger.warning("there is no name")
        return False
    try:
        async with pool.acquire() as con:
            query = """
                    SELECT EXISTS(SELECT 1 FROM products WHERE name = $1);
                    """
            res = await con.fetchval(query,name)
            logger.debug(f"{name=} {res=}")
            return bool(res) if res is not None else False
    except PostgresError as e:
        logger.error(f"invalid value {name=} {e}")
        return False


async def get_product_names(pool: Pool) -> list[str]:
    try:
        async with pool.acquire() as con:
            query = """
                    SELECT name FROM products LIMIT 10;
                    """
            res = await con.fetch(query)
            logger.debug(f" {res=}")
            return [row["name"] for row in res]
    except PostgresError as e:
        logger.error(f"Database error {e}",exc_info=True)
        return []


async def get_product(pool: Pool, name:str) -> dict | None:
    if not name:
        logger.warning("there is no name")
        return None
    try:
        async with pool.acquire() as con:
            query = """
                    SELECT price, description, tags, photo_id FROM products WHERE name = $1;
                    """
            res = await con.fetchrow(query,name)
            price = res["price"] 
            tags = res["tags"]
            if description := res["description"] is None:
                description = "no description"
            if photo_id := res["photo_id"] is None:
                photo_id = DEFUALT_IMG
            text = {
                "name": name,
                "price": price,
                "description": description,
                "tags": tags,
                "photo_id": photo_id
            }
            logger.debug(f"{name=} {res=}")
            return dict(text) if res is not None else None
    except PostgresError as e:
        logger.error(f"invalid value {name=} {e}")
        return None