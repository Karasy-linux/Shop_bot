from asyncpg import Pool, PostgresError, DataError, InterfaceError
from loguru import logger
from config import DEFUALT_IMG


# ============================================================
# USER & ADMIN
# ============================================================


async def is_admin(pool: Pool, chat_id: int) -> bool:
    if not chat_id:
        logger.warning("⚠️ there is no chat_id")
        return False
    try:
        async with pool.acquire() as con:
            query = """
                    SELECT is_admin FROM users WHERE chat_id = $1;
                    """
            res = await con.fetchval(query, chat_id)
            logger.debug(f"{chat_id=} {res=}")
            return bool(res) if res is not None else False
    except PostgresError as e:
        logger.error(f"❌ invalid value {chat_id=} {e}", exc_info=True)
        return False


async def add_user(pool: Pool, chat_id: int, username: str) -> None:
    try:
        async with pool.acquire() as con:
            query = """
                    INSERT INTO users(chat_id,username) VALUES($1,$2)
                    ON CONFLICT (chat_id) DO NOTHING;
                    """
            await con.execute(query, chat_id, username)
            logger.debug(f"👤 {chat_id=}, {username=}")
    except PostgresError as e:
        logger.error(f"❌ invalid values {e}", exc_info=True)


async def check_product_name(pool: Pool, name: str | None) -> bool:
    if not name:
        logger.warning("⚠️ there is no name")
        return False
    try:
        async with pool.acquire() as con:
            query = """
                    SELECT EXISTS(SELECT 1 FROM products WHERE name = $1);
                    """
            res = await con.fetchval(query, name)
            logger.debug(f"{name=} {res=}")
            return bool(res) if res is not None else False
    except PostgresError as e:
        logger.error(f"❌ invalid value {name=} {e}", exc_info=True)
        return False


async def my_profile(pool: Pool, chat_id: int) -> dict | None:
    query = """
            SELECT username, is_admin, balance, inventory FROM users
            WHERE chat_id = $1;
            """
    try:
        async with pool.acquire() as con:
            row = await con.fetchrow(query, chat_id)
            logger.debug(f"{row=}")
            return row
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        return


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
        logger.error(f"❌ Database error {e}", exc_info=True)
        return []


async def get_product(pool: Pool, name: str) -> dict | None:
    """
    The returned dictionary has the following structure:
    f"\U0001f4e6 <b>{product['name']}</b>\n\n"
            f"{product['description']}\n\n"
            f"\U0001f4b0 <b>price:</b> ${product['price']} \n"
            f"{product['tags']}"
    """
    if not name:
        logger.warning("⚠️ there is no name")
        return None
    try:
        async with pool.acquire() as con:
            query = """
                    SELECT name, price, description, tags, photo_id
                    FROM products WHERE name = $1
                    ORDER BY price DESC
                    LIMIT 4;
                    """
            res = await con.fetchrow(query, name)
            product = {}
            for key in res.keys():
                product[key] = res[key]
            price = int(res["price"])
            tags = res["tags"]
            description = res.get("description", "no description")
            photo_id = res.get("photo_id", DEFUALT_IMG)
            product = {
                "name": name,
                "price": price,
                "description": description,
                "tags": tags,
                "photo_id": photo_id,
            }
            logger.debug(f"{name=} {res=}")
            return product if res is not None else None
    except (PostgresError, DataError) as e:
        logger.error(f"❌ invalid value {name=} {e}", exc_info=True)
        return None


async def search_by_tags(pool: Pool, tags: str) -> list[str] | None:
    query = """
            SELECT name
            FROM products
            WHERE tags ILIKE $1;
            """
    try:
        async with pool.acquire() as con:
            names = await con.fetch(query, tags)
            logger.debug(f"{names=}, {tags=}")
            return [row["name"] for row in names]

    except DataError as e:
        logger.warning(f"⚠️ {e}", exc_info=True)

    except PostgresError as e:
        logger.warning(f"⚠️ {e}", exc_info=True)

    return None


async def show_inventory(pool: Pool, chat_id: int) -> str | None:
    query = """
            SELECT inventory FROM users WHERE chat_id = $1;
            """
    try:
        async with pool.acquire() as con:
            inventory = await con.fetchval(query, chat_id)
            logger.debug(f"{inventory=}")
            return inventory
    except DataError as e:
        logger.warning(f"⚠️ {e}", exc_info=True)
    except PostgresError as e:
        logger.warning(f"⚠️ {e}", exc_info=True)
    return None


# ============================================================
#                    CART
# ============================================================


async def show_total_price(pool: Pool, chat_id: int) -> int | None:
    query = """
            SELECT COALESCE(SUM(p.price), 0)
            FROM carts c
            JOIN products p ON c.name = p.name
            WHERE c.chat_id = $1;
            """
    try:
        async with pool.acquire() as con:
            total_price = await con.fetchval(query, chat_id)
            if total_price is not None:
                total_price = int(total_price)
            logger.info(f"💰 success return a total price in the cart {total_price=}")
            return total_price
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        return None


async def add_cart(pool: Pool, chat_id: int, name: str) -> None:
    if not name:
        logger.warning("⚠️ there is no name")
        return
    try:
        async with pool.acquire() as con:
            query = "INSERT INTO carts(chat_id,name) VALUES($1,$2)"
            await con.execute(query, chat_id, name)
            logger.info(f"🛒 add to cart: {chat_id=}, {name=}")
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)


async def check_user_cart(pool: Pool, chat_id: int, name: str) -> bool:
    if not name or not chat_id:
        return False
    query = """
            SELECT EXISTS(SELECT 1 FROM carts
            WHERE chat_id = $1 AND name = $2);
            """
    try:
        async with pool.acquire() as con:
            res = await con.fetchval(query, chat_id, name)
    except PostgresError as e:
        logger.warning(f"⚠️ {e}", exc_info=True)
        return False
    logger.debug(f"{res=}")
    return bool(res)


async def show_names_cart(pool: Pool, chat_id: int) -> list[str] | None:
    if not chat_id:
        logger.warning("⚠️ not have chat_id")
        return
    query = """
            SELECT name FROM carts WHERE chat_id = $1;
            """
    try:
        async with pool.acquire() as con:
            rows = await con.fetch(query, chat_id)
            names = [row["name"] for row in rows]
            logger.debug(f"{names=}")
            return names
    except PostgresError as e:
        logger.warning(f"⚠️ don't get products from cart for {chat_id=}\n{e}", exc_info=True)
        return


async def del_product_cart(pool: Pool, chat_id: int, name: str) -> bool:
    query = """
            DELETE FROM carts WHERE chat_id = $1 AND name = $2
            """
    try:
        async with pool.acquire() as con:
            await con.execute(query, chat_id, name)
            logger.info(f"🗑️ {chat_id=} deleted {name}")
            return True
    except PostgresError as e:
        logger.warning(f"⚠️ {e}", exc_info=True)
        return False


async def buy_product(
    pool: Pool,
    chat_id: int,
    names: list[str],
    price: int,
) -> bool:
    if not names:
        logger.warning(f"⚠️ No products in the cart for user {chat_id}")
        return False
    query_update_user = """
        UPDATE users 
        SET balance = balance - $1, 
            inventory = inventory || $2 
        WHERE chat_id = $3;
    """
    query_delete_cart = """
        DELETE FROM carts WHERE chat_id = $1;
    """

    try:
        async with pool.acquire() as con:   
            current_balance = await show_balance(pool,chat_id)
        
            if current_balance is None:
                logger.warning(f"⚠️ User {chat_id} not found in database")
                return False
                
            if current_balance < price:
                logger.warning(f"⚠️ User {chat_id} insufficient funds. Has: {current_balance}, Needs: {price}")
                return False

            await con.execute(query_update_user, price, names, chat_id)
            await con.execute(query_delete_cart, chat_id)
            logger.success(f"✅ User: {chat_id} successfully paid {price} Stars for products")
            return True

    except Exception as e:
        logger.error(f"❌ Transaction failed for user {chat_id}: {e}", exc_info=True)
        return False


# ============================================================
#                  BALANCE
# ============================================================


async def show_balance(pool: Pool, chat_id: int) -> int | None:
    if not chat_id:
        logger.warning("⚠️ there is no chat_id")
        return
    query = "SELECT balance FROM users WHERE chat_id = $1"
    try:
        async with pool.acquire() as con:
            balance = await con.fetchval(query, chat_id)
            if balance is not None:
                balance = int(balance)
            logger.debug(f"{chat_id=}\nbalance ${balance}")
            return balance
    except PostgresError as e:
        logger.warning(f"⚠️ {e}", exc_info=True)
        return None


async def change_balance(pool: Pool, chat_id: int, balance: int, pay: int) -> bool:
    if balance + pay < 0:
        logger.warning(f"⚠️ balance + top_up < 0 {balance=}, {pay=}")
        return False
    new_balance = balance + pay
    query = """
            UPDATE users SET balance = $1 WHERE chat_id = $2;
            """
    try:
        async with pool.acquire() as con:
            await con.execute(query, new_balance, chat_id)
            logger.info(f"💰 balance updated: {balance} → {new_balance}")
            return True
    except (PostgresError, DataError) as e:
        logger.warning(f"⚠️ can't change balance {e}", exc_info=True)
        return False
