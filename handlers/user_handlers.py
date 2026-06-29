from database import service 
from keyboards import user_kb as ukb
from keyboards.user_kb import AddCart, DelCart
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from asyncpg import Pool
from loguru import logger
from config import DEFUALT_IMG

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message,pool: Pool) -> None:
    if message.from_user:
        username = message.from_user.username or "user"
    else:
        username = "user"
    text = f"Hello, @{username}!\n This is the shop bot"
    await service.add_user(pool,message.chat.id,username)
    await message.reply(text=text,reply_markup=ukb.catalog)


@user_router.message(Command("catalog"))
async def cmd_catalog(message: Message) -> None:
    text = "CATALOG"
    await message.reply(text=text,reply_markup=ukb.tables)


@user_router.callback_query(F.data == "tables")
async def cmd_show(callback: CallbackQuery, pool: Pool) -> None:
    product_names = await service.get_product_names(pool)
    chat_id = callback.from_user.id

    await callback.message.delete()
    for _, name in enumerate(product_names):
        product_info = await service.get_product(pool, name)
        in_cart = await service.check_user_cart(pool,chat_id,name)
        if product_info and not in_cart:
            await callback.message.answer_photo(
                photo=product_info.get("photo_id",DEFUALT_IMG),
                caption=(
                    f"📦 <b>{name}</b>\n"
                    f"{product_info.get('description',"is cool product")}\n"
                    f"💰 <b>price:</b> ${product_info['price']}\n"
                    f"{product_info.get('tags',"home")}"
                ),
                parse_mode="HTML",
                reply_markup=ukb.add_product_kb(name)
            )
    await callback.answer()


@user_router.callback_query(AddCart.filter())
async def add_cart(callback:CallbackQuery, callback_data:AddCart, pool:Pool) -> None:
    await callback.answer()
    product_name = callback_data.product_name
    chat_id = callback.from_user.id
    in_cart = await service.check_user_cart(pool,chat_id,product_name)
    logger.debug(f"{in_cart=}")
    if in_cart:
        await callback.message.answer(text="This product has already been added to your cart")
        return
    try:
        await service.add_cart(pool,chat_id,product_name)
        await callback.message.delete()
        await callback.message.answer(text=f"success add to cart the product: *{product_name}*",parse_mode="MarkdownV2")
        logger.info(f"add to cart by {chat_id}")
        return
    except ValueError as e:
        logger.warning(f"incorect value for add_cart, {e}",exc_info=True)    
        await callback.message.answer(text="unsuccess! product is not added")
        return 
  

@user_router.message(Command("my_cart"))
async def show_cart(message: Message,pool: Pool, price = 0.0):
    chat_id = message.chat.id
    rows = await service.show_name_cart(pool,chat_id)
    product_names = [row['name'] for row in rows]
    if not product_names:
        await message.answer("You do not have a products in the cart")
        return
    for _, name in enumerate(product_names):
        product_info = await service.get_product(pool, name)
        in_cart = await service.check_user_cart(pool,chat_id,name)
        if product_info and in_cart:
            await message.answer_photo(
                photo=product_info.get("photo_id",DEFUALT_IMG),
                caption=(
                    f"📦 <b>{name}</b>\n"
                    f"{product_info.get('description',"is cool product")}\n"
                    f"💰 <b>price:</b> ${product_info['price']}\n"
                    f"{product_info.get('tags',"home")}"
                ),
                parse_mode="HTML",
                reply_markup=ukb.del_product_kb(name)
            )
            price += product_info["price"]
    balance = await service.show_balance(pool,chat_id)
    text = f"buy continue to paymant ${price}\n my balance: {balance}"
    await message.answer(text=text,reply_markup=ukb.buy_kb)


@user_router.callback_query(DelCart.filter())
async def del_cart(callback: CallbackQuery, callback_data:DelCart, pool:Pool) -> None:
    await callback.answer()
    chat_id = callback.from_user.id
    product_name = callback_data.product_name
    check = await service.del_product_cart(pool,chat_id,product_name)
    if not check:
        await callback.message.answer("You don't have products in the cart")
        return 
    await callback.message.delete()
    text = f"you delete to *{product_name}* from the cart"
    await callback.message.answer(text,parse_mode="MarkdownV2")
    