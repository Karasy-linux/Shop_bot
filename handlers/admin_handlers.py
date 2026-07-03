from database import admin_queries as adb
from database import service as service
from keyboards import admin_kb as akb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from asyncpg import Pool, PostgresError
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
async def cmd_admin(message: Message, pool: Pool) -> None:
    chat_id = message.chat.id
    try:
        if await service.is_admin(pool, chat_id):
            text = "👋 Welcome, admin!"
            await message.reply(text=text, reply_markup=akb.tables)
            logger.info(f"👑 Admin logged in: {chat_id}")
        else:
            text = "⛔ You aren't admin"
            await message.reply(text=text)
            logger.warning(f"⛔ Unauthorized admin attempt: {chat_id}")
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await message.answer("❌ Database error. Please try again later.")


@admin_router.callback_query(F.data == "add:product")
async def add_(callback: CallbackQuery) -> None:
    await callback.answer()
    text = "📦 Let's add a new product to the catalog! Please choose the parameter you want to set first."
    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=akb.add_name_kb)
    logger.info(f"➕ Admin started adding product: {callback.from_user.id}")


@admin_router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    text = "❌ Operation cancelled."
    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=akb.tables)
    logger.info(f"❌ Operation cancelled by {callback.from_user.id}")


@admin_router.callback_query(F.data == "set:name")
async def name_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "✏️ Please enter the name of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.name)


@admin_router.message(SetStates.name)
async def set_name(message: Message, state: FSMContext) -> None:
    name = message.text
    if not name or len(name) > 50:
        await message.answer(
            text="❌ Invalid product name. Name must be between 1 and 50 characters."
        )
        await state.clear()
        await message.answer(text="❌ Operation cancelled.", reply_markup=akb.add_name_kb)
        return

    await state.update_data(name=name)
    await message.answer(text=f"✅ Name set to: {name}")
    await message.answer(text="💰 Please enter the price of the product.", reply_markup=akb.add_price_kb)
    logger.info(f"✏️ Product name set: {name}")


@admin_router.callback_query(F.data == "set:price")
async def price_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "💰 Please enter the price of the product (in Telegram Stars)."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.price)


@admin_router.message(SetStates.price)
async def set_price(message: Message, state: FSMContext) -> None:
    try:
        price = int(message.text)
        if price < 0:
            raise ValueError("price must be non-negative")
    except (ValueError, TypeError) as e:
        logger.warning(f"⚠️ Invalid price input: {message.text} — {e}")
        await message.answer(text="❌ Invalid price. Please enter a valid positive number.")
        return
    await state.update_data(price=price)
    await message.answer(text=f"✅ Price set to: {price} ⭐️")
    text = "🏷️ Please send tags of the product."
    await message.answer(text=text, reply_markup=akb.add_tags_kb)
    logger.info(f"💰 Product price set: {price}")


@admin_router.callback_query(F.data == "set:tags")
async def tags_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "🏷️ Please enter the tags of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.tags)


@admin_router.message(SetStates.tags)
async def set_tags(message: Message, state: FSMContext) -> None:
    await state.update_data(tags=message.text)
    await message.answer(text=f"✅ Tags set to: {message.text}")
    text = "📝 Please enter the description of the product."
    await message.answer(text=text, reply_markup=akb.add_description_kb)


@admin_router.callback_query(F.data == "set:description")
async def description_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "📝 Please enter the description of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.description)


@admin_router.message(SetStates.description)
async def set_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer(text=f"✅ Description set to: {message.text}")
    text = "📸 Please send a photo of the product."
    await message.answer(text=text, reply_markup=akb.add_photo_kb)


@admin_router.callback_query(F.data == "set:skip")
async def skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "📸 Please send the photo of the product."
    await callback.message.delete()
    await callback.answer(text=text, reply_markup=akb.add_photo_kb)
    await state.set_state(SetStates.photo)


@admin_router.callback_query(F.data == "set:photo")
async def photo_fsm(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "📸 Please send the photo of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(SetStates.photo)


@admin_router.message(SetStates.photo)
async def set_photo(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer(text="❌ Invalid photo. Please send a valid photo.")
        return
    try:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
    except (TypeError, IndexError) as e:
        logger.warning(f"⚠️ Photo error: {e}", exc_info=True)
        await message.answer(text="❌ Invalid photo. Please send a valid photo.")
        return
    await message.answer(text=f"✅ Photo set", reply_markup=akb.add_finally_kb)
    logger.debug(f"📸 {photo_id=}, {state=}")


@admin_router.callback_query(F.data == "set:finish")
async def skip_finally(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    data = await state.get_data()
    logger.debug(f"{data=}")
    name = data.get("name", "product")
    price = data.get("price", 1000)
    tags = data.get("tags", "all")
    description = data.get("description", None)
    photo_id = data.get("photo_id", None)
    try:
        await adb.add_product(pool, name, price, tags, description, photo_id)
        await state.clear()
        text = "✅ Product successfully added to the catalog!"
        await callback.message.delete()
        await callback.answer(text=text)
        logger.success(f"✅ Product added: {name}, price={price}")
    except (PostgresError, ValueError) as e:
        logger.warning(f"⚠️ Failed to add product: {e}", exc_info=True)
        await callback.message.answer("❌ Failed to add product. Please try again.")
        await state.clear()


@admin_router.callback_query(F.data == "edit:product")
async def edit_product(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    try:
        products = await service.get_product_names(pool)
        text = (
            f"✏️ Let's edit a product in the catalog!\n"
            f"Available products: {', '.join(products)}"
        )
        await callback.message.delete()
        await callback.message.answer(text=text, reply_markup=akb.edit_product_kb)
        logger.info(f"✏️ Admin editing product: {callback.from_user.id}")
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await callback.message.answer("❌ Database error. Please try again later.")


@admin_router.callback_query(F.data == "edit:set:product")
async def edit_set_name_product(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "✏️ Please enter the name of the product you want to edit."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.name)


@admin_router.message(EditStatus.name)
async def set_product_name(message: Message, state: FSMContext, pool: Pool) -> None:
    try:
        if not await service.check_product_name(pool, message.text):
            await message.answer(text="❌ Invalid product name. Please enter a valid name.")
            await state.clear()
            await message.answer(text="❌ Operation cancelled.", reply_markup=akb.edit_product_kb)
            return
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await state.clear()
        await message.answer(text="❌ Database error. Please try again.")
        return
    await state.update_data(name=message.text)
    await message.answer(text=f"✅ Name set to: {message.text}")
    text = "💰 Please enter the new price of the product."
    await message.answer(text=text, reply_markup=akb.edit_price_kb)
    logger.info(f"✏️ Editing product: {message.text}")


@admin_router.callback_query(F.data == "edit:price")
async def edit_product_price(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "💰 Please enter the new price of the product (in Telegram Stars)."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.price)


@admin_router.message(EditStatus.price)
async def edit_price(message: Message, state: FSMContext) -> None:
    try:
        price = int(message.text)
        if price < 0:
            raise ValueError("price must be non-negative")
    except (ValueError, TypeError) as e:
        logger.warning(f"⚠️ Invalid price input: {message.text} — {e}")
        await message.answer(text="❌ Invalid price. Please enter a valid positive number.")
        return
    await state.update_data(price=price)
    await message.answer(text=f"✅ Price set to: {price} ⭐️")
    text = "🏷️ Please send new tags of the product."
    await message.answer(text=text, reply_markup=akb.edit_tags_kb)
    logger.info(f"💰 Edited price: {price}")


@admin_router.callback_query(F.data == "edit:tags")
async def edit_product_tags(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "🏷️ Please enter the new tags of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.tags)


@admin_router.message(EditStatus.tags)
async def edit_tags(message: Message, state: FSMContext) -> None:
    await state.update_data(tags=message.text)
    await message.answer(text=f"✅ Tags set to: {message.text}")
    text = "📝 Please enter the new description of the product."
    await message.answer(text=text, reply_markup=akb.edit_description_kb)


@admin_router.callback_query(F.data == "edit:description")
async def edit_product_description(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "📝 Please enter the new description of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.description)


@admin_router.message(EditStatus.description)
async def edit_description(message: Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await message.answer(text=f"✅ Description set to: {message.text}")
    text = "📸 Please send a new photo of the product."
    await message.answer(text=text, reply_markup=akb.edit_photo_kb)


@admin_router.callback_query(F.data == "edit:photo")
async def edit_product_photo(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    text = "📸 Please send the new photo of the product."
    await callback.message.delete()
    await callback.message.answer(text=text)
    await state.set_state(EditStatus.photo)


@admin_router.message(EditStatus.photo)
async def edit_photo(message: Message, state: FSMContext) -> None:
    if not message.photo:
        await message.answer(text="❌ Invalid photo. Please send a valid photo.")
        return
    try:
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
    except (TypeError, IndexError) as e:
        logger.warning(f"⚠️ Photo error: {e}", exc_info=True)
        await message.answer(text="❌ Invalid photo. Please send a valid photo.")
        return
    await message.answer(text=f"✅ Photo set", reply_markup=akb.edit_finally_kb)
    logger.debug(f"📸 {photo_id=}, {state=}")


@admin_router.callback_query(F.data == "edit:skip")
async def edit_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    states = [
        EditStatus.name,
        EditStatus.price,
        EditStatus.tags,
        EditStatus.description,
        EditStatus.photo,
    ]
    state_kb = [
        akb.edit_price_kb,
        akb.edit_tags_kb,
        akb.edit_description_kb,
        akb.edit_photo_kb,
        akb.edit_finally_kb,
    ]

    current_state = await state.get_state()

    if current_state in states:
        current_index = states.index(current_state)
        next_index = current_index + 1

        await callback.message.delete()

        if next_index < len(states):
            await state.set_state(states[next_index])

            next_kb = state_kb[current_index]
            field_name = states[next_index].state.split(":")[-1]

            text = f"✏️ Please send the {field_name} of the product."
            await callback.message.answer(text=text, reply_markup=next_kb)
        else:
            await state.clear()
            text = "✅ You have completed all the steps. Please finish the editing process."
            await callback.message.answer(text=text, reply_markup=akb.edit_finally_kb)


@admin_router.callback_query(F.data == "edit:finish")
async def edit_finally(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    data = await state.get_data()
    logger.debug(f"{data=}")

    name = str(data.get("name", "product"))
    price = data.get("price", None)
    tags = str(data.get("tags", None))
    description = str(data.get("description", None))
    photo_id = str(data.get("photo_id", None))

    if price is not None:
        try:
            price = int(price)
        except (ValueError, TypeError) as e:
            logger.warning(f"⚠️ Invalid price in edit data: {price} {e}")
            await callback.answer(text="❌ Invalid price value.")
            await state.clear()
            return

    try:
        await adb.edit_product(pool, name, price, tags, description, photo_id)
        await state.clear()
        text = "✅ Product successfully edited!"
        await callback.message.delete()
        await callback.answer(text=text)
        logger.success(f"✅ Product edited: {name}")
    except (PostgresError, ValueError) as e:
        logger.warning(f"⚠️ Failed to edit product: {e}", exc_info=True)
        await callback.answer(text="❌ Failed to edit the product. Please try again.")
        await state.clear()


@admin_router.callback_query(F.data == "delete:product")
async def delete_product(callback: CallbackQuery, state: FSMContext, pool: Pool) -> None:
    await callback.answer()
    try:
        products = await service.get_product_names(pool)
        text = f"🗑️ Please enter the name of the product you want to delete.\nAvailable products: {', '.join(products)}"
        await callback.message.delete()
        await callback.message.answer(text=text)
        await state.set_state(DeleteProduct.name)
        logger.info(f"🗑️ Admin deleting product: {callback.from_user.id}")
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await callback.message.answer("❌ Database error. Please try again later.")


@admin_router.message(DeleteProduct.name)
async def delete_product_name(message: Message, pool: Pool, state: FSMContext) -> None:
    name = message.text
    try:
        if not await service.check_product_name(pool, name):
            await message.answer(text="❌ Product not found. Please enter a valid product name.")
            await message.answer(text="❌ Operation cancelled.")
            await state.clear()
            return
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await state.clear()
        await message.answer(text="❌ Database error. Please try again.")
        return
    try:
        await adb.delete_product(pool, name)
        await state.clear()
        await message.answer(text=f"✅ Product '{name}' deleted successfully.")
        logger.success(f"🗑️ Product deleted: {name}")
    except (PostgresError, ValueError) as e:
        await state.clear()
        logger.warning(f"⚠️ Failed to delete product: {e}", exc_info=True)
        await message.answer(text="❌ Failed to delete product. Please try again.")
