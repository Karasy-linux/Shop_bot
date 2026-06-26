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
    
    await callback.message.delete()
    for i in range(len(product_names)):
        product_name = product_names[i]
        product_info = await service.get_product(pool, product_name)
        if product_info:
            await callback.message.answer_photo(
                photo=product_info.get("photo_id",DEFUALT_IMG),
                caption=(
                    f"📦 <b>{product_info['name']}</b>\n"
                    f"{product_info.get('description',"is cool product")}\n"
                    f"💰 <b>price:</b> ${product_info['price']}\n"
                    f"{product_info.get('tags',"home")}"
                ),
                parse_mode="HTML",
                reply_markup=ukb.add_product_kb(product_info["name"]) #type:ignore
            )
    await callback.answer()


@user_router.callback_query(AddCart.filter())
async def add_cart(callback:CallbackQuery, callback_data:AddCart, pool:Pool) -> None:
    await callback.answer()
    product_name = callback_data.product_name
    chat_id = callback.from_user.id
    try:
        await service.add_cart(pool,chat_id,product_name)
    except ValueError as e:
        logger.warning(f"incorect value for add_cart, {e}",exc_info=True)    
        await callback.message.answer(text="unsuccess product is added to cart")
        return 
    await callback.message.answer(text=f"success add to cart the product: *{product_name}*",parse_mode="MarkdownV2")
    logger.info(f"add to cart by {chat_id}")
  


