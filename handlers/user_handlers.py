import asyncio
import aiogram
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from asyncpg import Pool
import database.service as service
import keyboards.user_kb as ukb


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
async def cmd_show(callback: CallbackQuery) -> None:
    await callback.message.answer("These list tables:") #type: ignore 
    await callback.answer()




