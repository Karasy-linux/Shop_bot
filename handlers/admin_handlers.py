from database import admin_queries as adb
from database import service as service
from keyboards import admin_kb as akb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from asyncpg import Pool
from loguru import logger


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


@admin_router.callback_query(F.data == "cancel")
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
    name = message.text
    if not name:
        await message.answer(text="Invalid product name. Please enter a valid name.")
        await state.clear()
        await message.answer(text="Operation cancelled.", reply_markup=akb.add_name_kb)
        return
    await state.update_data(name=name)
    await message.answer(text=f"Name set to: {name}")
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
    await message.answer(text=f"Tags set to: {message.text}")
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
    await message.answer(text=f"Description set to: {message.text}")
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


@admin_router.callback_query(F.data == "edit:product")
async def edit_product(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    products = await service.get_product_names(pool)
    text = (f"Let's edit a product in the catalog! Please choose the parameter you want to edit first."
            f"\nAvailable products: {', '.join(products)}")
    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=akb.edit_product_kb)
   

@admin_router.callback_query(F.data == "edit:set:product")
async def edit_set_name_product(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Let's edit a product in the catalog! Please choose the parameter you want to edit first."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.name)


@admin_router.message(EditStatus.name)
async def set_product_name(message: Message, state: FSMContext,pool: Pool) -> None:
    if not await service.check_product_name(pool,message.text):
        await message.answer(text="Invalid product name. Please enter a valid name.")
        await state.clear()
        await message.answer(text="Operation cancelled.", reply_markup=akb.edit_product_kb)
        return
    await state.update_data(name=message.text)
    await message.answer(text=f"Name set to: {message.text}")
    text = "Please enter the price of the product."
    await message.answer(text=text, reply_markup=akb.edit_price_kb)



@admin_router.callback_query(F.data == "edit:price")
async def edit_product_price(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please enter the price of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.price)


@admin_router.message(EditStatus.price)
async def edit_price(message: Message, state: FSMContext) -> None:
    try:
        price = float(message.text)
    except ValueError:
        await message.answer(text="Invalid price. Please enter a valid number.")
        return
    await state.update_data(price=price)
    await message.answer(text=f"Price set to: {price}")
    text = "Please send tags of the product."
    await message.answer(text=text, reply_markup=akb.edit_tags_kb)



@admin_router.callback_query(F.data == "edit:tags")
async def edit_product_tags(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please enter the tags of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.tags)


@admin_router.message(EditStatus.tags)
async def edit_tags(message: Message, state: FSMContext) -> None:
    await state.update_data(tags=message.text)
    await message.answer(text=f"Tags set to: {message.text}")
    text = "Please enter the description of the product."
    await message.answer(text=text, reply_markup=akb.edit_description_kb)



@admin_router.callback_query(F.data == "edit:description")
async def edit_product_description(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please enter the description of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.description)


@admin_router.message(EditStatus.description)
async def edit_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer(text=f"Description set to: {message.text}")
    text = "Please send a photo of the product."
    await message.answer(text=text, reply_markup=akb.edit_photo_kb)



@admin_router.callback_query(F.data == "edit:photo")
async def edit_product_photo(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "Please send the photo of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.photo)


@admin_router.message(EditStatus.photo)
async def edit_photo(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer(text="Invalid photo. Please enter a valid photo.")
        return
    try:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
    except TypeError:
        await message.answer(text="Invalid photo. Please enter a valid photo.")
        return
    await message.answer(text=f"photo set to: {photo_id}",reply_markup=akb.edit_finally_kb)
    logger.debug(f"{photo_id=}, {state}")


@admin_router.callback_query(F.data == "edit:skip")
async def edit_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    states = [EditStatus.name, EditStatus.price, EditStatus.tags, EditStatus.description, EditStatus.photo]
    state_kb = [akb.edit_product_kb,akb.edit_price_kb, akb.edit_tags_kb, akb.edit_description_kb, akb.edit_photo_kb]
    current_state = await state.get_state()
    if current_state in states:
        next_state_index = states.index(current_state) + 2
        if next_state_index < len(states):
            next_state_kb = state_kb[next_state_index]
            text = f"Please send the {states[next_state_index].state[11:]} of the product."
            await callback.message.delete()
            await callback.message.answer(text=text, reply_markup=next_state_kb)
        else:
            text = "You have completed all the steps. Please finish the editing process."
            await callback.message.delete()
            await callback.message.answer(text=text, reply_markup=akb.edit_finally_kb)


@admin_router.callback_query(F.data == "edit:finish")
async def edit_finally(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    data = await state.get_data()
    logger.debug(f"{data=}")
    name = str(data.get("name", "product"))
    price = (data.get("price", None))
    tags = str(data.get("tags", None))
    description = str(data.get("description", None))
    photo_id = str(data.get("photo_id", None))
    try:
        await adb.edit_product(pool,name,price,tags,description,photo_id)
    except ValueError as e:
        logger.warning(f"not correctly response,{e}",exc_info=True)
    text = "Success edit the product!"
    await callback.message.delete()
    await callback.answer(text=text)



@admin_router.callback_query(F.data == "delete:product")
async def delete_product(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    products = await service.get_product_names(pool)
    text = f"Please enter the name of the product you want to delete.\nAvailable products: {', '.join(products)}"
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(DeleteProduct.name)


@admin_router.message(DeleteProduct.name)
async def delete_product_name(message: Message, pool: Pool) -> None:
    name = message.text
    if not service.check_product_name(pool,name):
        await message.answer(text="Product not found. Please enter a valid product name.")
        await message.answer(text="Operation cancelled.")
        return
    try:
        await adb.delete_product(pool,name)
    except ValueError as e:
        logger.warning(f"not correctly response,{e}",exc_info=True)
    
