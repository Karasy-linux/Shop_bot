from asyncpg import Pool, PostgresError
from loguru import logger
from config import DEFUALT_IMG 
from database import service

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
    """
    The returned dictionary has the following structure:
    f"📦 <b>{product['name']}</b>\n\n"
            f"{product['description']}\n\n"
            f"💰 <b>price:</b> ${product['price']} \n"
            f"{product['tags']}"
    """
    if not name:
        logger.warning("there is no name")
        return None
    try:
        async with pool.acquire() as con:
            query = """
                    SELECT name,price, description, tags, photo_id 
                    FROM products WHERE name = $1
                    ORDER BY price DESC
                    LIMIT 4;
                    """
            res = await con.fetchrow(query,name)
            product = {}
            for key in res.keys():
                product[key] = res[key]
            price = res["price"] 
            tags = res["tags"]
            description = res.get("description", "no description")
            photo_id = res.get("photo_id", DEFUALT_IMG)
            product = {
                "name": name,
                "price": price,
                "description": description,
                "tags": tags,
                "photo_id": photo_id
            }
            logger.debug(f"{name=} {res=}")
            return product if res is not None else None
    except PostgresError as e:
        logger.error(f"invalid value {name=} {e}")
        return None
    

async def add_cart(pool:Pool,chat_id:int, name:str) -> None:
    if not name:
        logger.warning("there is no name")
        return
    try:
        async with pool.acquire() as con:
            query = "INSERT INTO carts(chat_id,name) VALUES($1,$2)"
            await con.execute(query,chat_id,name)
            logger.info(f"add to cart:{chat_id=},{name=}")
    except PostgresError as e:
        logger.error(f"{e}",exc_info=True)  