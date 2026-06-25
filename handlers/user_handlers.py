from database import service 
from keyboards import user_kb as ukb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from asyncpg import Pool

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
                photo=product_info["photo_id"],
                caption=(
                    f"📦 <b>{product_info['name']}</b>\n"
                    f"{product_info['description']}\n"
                    f"💰 <b>price:</b> ${product_info['price']}\n"
                    f"{product_info['tags']}"
                ),
                parse_mode="HTML"
            )
    await callback.answer()




