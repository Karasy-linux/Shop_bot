import asyncio
import aiogram
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from asyncpg import Pool
from loguru import logger

import database.admin_queries as adb
import database.service as service
import keyboards.admin_kb as akb

class SetStates(StatesGroup):
    photo = State()
    name = State()
    price = State()
    description = State()
    tags = State()

class EditStatus(SetStates):
    photo = State()
    name = State()
    price = State()
    description = State()
    tags = State()

class DeleteProduct(SetStates):
    name = State()


admin_router = Router()

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message,pool: Pool) -> None:
    if await service.is_admin(pool, message.chat.id):
        text = "Welcome, admin!"
        await message.reply(text=text,reply_markup=akb.tables)
    else:
        text = "You aren't admin"
        await message.reply(text=text)        
        return



@admin_router.callback_query(F.data == "add:product")
async def add_(callback: CallbackQuery) -> None:
    await callback.answer()
    text = "Let's add a new product to the catalog! Please choose the parameter you want to set first."

    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=akb.add_name_kb) 


@admin_router.callback_query(F.data == "set:cancel")
async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    text = "Operation cancelled."
    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=akb.tables)



@admin_router.callback_query(F.data == "set:name")
async def name_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please enter the name of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.name)
    

@admin_router.message(SetStates.name)
async def set_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await message.answer(text=f"Name set to: {message.text}")
    await message.answer(text="Please enter the price of the product.", reply_markup=akb.add_price_kb)



@admin_router.callback_query(F.data == "set:price")
async def price_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please enter the price of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.price)


@admin_router.message(SetStates.price)
async def set_price(message: Message, state: FSMContext) -> None:
    try:
        price = float(message.text)
    except ValueError:
        await message.answer(text="Invalid price. Please enter a valid number.")
        return 
    await state.update_data(price=price)
    await message.answer(text=f"Price set to: {price}")
    text = "Please send tags of the product."
    await message.answer(text=text, reply_markup=akb.add_tags_kb)



@admin_router.callback_query(F.data == "set:tags")
async def tags_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please enter the tags of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.tags)


@admin_router.message(SetStates.tags)
async def set_tags(message: Message, state: FSMContext) -> None:
    await state.update_data(tags=message.text)
    await message.answer(text=f"Tegs set to: {message.text}")
    text = "Please enter the description of the product."
    await message.answer(text=text, reply_markup=akb.add_description_kb)
    
        

@admin_router.callback_query(F.data == "set:description")
async def description_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please enter the description of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.description)


@admin_router.message(SetStates.description)
async def set_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text) 
    await message.answer(text=f"description set to: {message.text}")
    text = "Please send a photo of the product."
    await message.answer(text=text, reply_markup=akb.add_photo_kb)


@admin_router.callback_query(F.data == "set:skip")
async def skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please send the photo of the product."
    await callback.answer(text=text, reply_markup=akb.add_photo_kb)


@admin_router.callback_query(F.data == "set:photo")
async def photo_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please send the photo of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.photo)


@admin_router.message(SetStates.photo)
async def set_photo(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer(text="Invalid photo. Please enter a valid photo.")
        return
    try:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
    except TypeError:
        await message.answer(text="Invalid photo. Please enter a valid photo.")
        return 
    await message.answer(text=f"photo set to: {photo_id}",reply_markup=akb.add_finally_kb)
    logger.debug(f"{photo_id=}, {state}")


@admin_router.callback_query(F.data == "set:finish")
async def skip_finally(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    data = await state.get_data()
    logger.debug(f"{data=}")
    name = data.get("name", "product")
    price = data.get("price", 1000.0)
    tags = data.get("tags", "all")
    description = data.get("description", None)
    photo_id = data.get("photo_id", None)
    try:
        await adb.add_product(pool,name,price,tags,description,photo_id)
    except ValueError as e:
        logger.warning(f"not correctly response,{e}",exc_info=True)
    text = "Success sets to store the product!"
    await callback.message.delete()
    await callback.answer(text=text)







    
