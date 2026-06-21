from asyncpg import Pool, PostgresError
from loguru import logger


async def add_product(pool: Pool, name:str, price:float, tags:str,
        description=None | str, photo_id=None | str) -> None:
    try:
        async with pool.acquire() as con: #type: ignore
            query = """
                INSERT INTO
                products(name,price,tags,description,photo_id)
                VALUES($1,$2,$3,$4,$5)
                    """
            await con.execute(query,name,price,tags,description,photo_id)
            logger.success("admin success add a new product in the catalog")
    except PostgresError as e:
        logger.error(f"{e}",exc_info=True)


async def edit_product(pool: Pool, name:str ,price=None | float, tags=None | str,
                       new_description=None | str, photo_id=None | str) -> None:
    update_product = {}
    if price is not None:
        update_product["price"] = price
    if tags is not None:
        update_product["tags"] = tags
    if  new_description is not None:
        update_product["description"] = new_description
    if photo_id is not None:
        update_product["photo_id"] = photo_id
    if not update_product:
        logger.warning("there is no parameters to update")
        return

    set_parst = []
    values = []
    counter = 1
    for key, value in update_product.items():
        set_parst.append(f"{key} = ${counter}")
        values.append(value)
        counter += 1
    set_query = ", ".join(set_parst)
    values.append(name)

    try:
        async with pool.acquire() as con: #type: ignore
            query = f"""
                    UPDATE products SET {set_query} WHERE name = ${counter};
                    """
            await con.execute(query, *values)
            logger.info(f"success update product {name=}")
    except PostgresError as e:
        logger.error(f"invalid {name=} {e}",exc_info=True)


async def delete_product(pool: Pool, name:str) -> None:
    try:
        async with pool.acquire() as con: #type: ignore
            query = """
                    DELETE FROM products WHERE name = $1 ON CONFLICT (name) DO NOTHING;
                    """
            await con.execute(query,name)
            logger.info(f"success delete product {name=}")
    except PostgresError as e:
        logger.error(f"invalid {name=} {e}",exc_info=True)
