from asyncpg import Pool, PostgresError, DataError
from loguru import logger


async def add_product(
    pool: Pool,
    name: str,
    price: int,
    tags: str,
    description=None | str,
    photo_id=None | str,
) -> None:
    try:
        async with pool.acquire() as con:
            query = """
                INSERT INTO
                products(name,price,tags,description,photo_id)
                VALUES($1,$2,$3,$4,$5)
                    """
            await con.execute(query, name, price, tags, description, photo_id)
            logger.success("✅ Admin added a new product to the catalog")
    except (PostgresError, DataError) as e:
        logger.error(f"❌ {e}", exc_info=True)


async def edit_product(
    pool: Pool,
    name: str,
    price: int | None = None,
    tags: str | None = None,
    new_description: str | None = None,
    photo_id: str | None = None,
) -> None:
    update_product = {}

    if price is not None:
        update_product["price"] = price

    if tags is not None and tags != "None":
        update_product["tags"] = tags

    if new_description is not None and new_description != "None":
        update_product["description"] = new_description

    if photo_id is not None and photo_id != "None":
        update_product["photo_id"] = photo_id

    if not update_product:
        logger.warning("⚠️ no fields to update")
        return

    set_parts = [f"{key} = ${i}" for i, key in enumerate(update_product.keys(), start=1)]
    set_query = ", ".join(set_parts)

    values = list(update_product.values())
    values.append(name)
    where_counter = len(values)

    query = f"UPDATE products SET {set_query} WHERE name = ${where_counter};"
    try:
        async with pool.acquire() as con:
            await con.execute(query, *values)
            logger.info(f"✅ updated product {name=} fields: {list(update_product.keys())}")
    except (PostgresError, DataError) as e:
        logger.error(f"❌ invalid {name=} {e}", exc_info=True)


async def delete_product(pool: Pool, name: str | None) -> None:
    if not name:
        logger.warning("⚠️ there is no name")
        return
    try:
        async with pool.acquire() as con:
            query = """
                    DELETE FROM products WHERE name = $1;
                    """
            await con.execute(query, name)
            logger.info(f"🗑️ deleted product {name=}")
    except PostgresError as e:
        logger.error(f"❌ invalid {name=} {e}", exc_info=True)
