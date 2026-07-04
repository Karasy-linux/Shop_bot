from database import service
from keyboards import user_kb as ukb
from keyboards.user_kb import AddCart, DelCart
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from asyncpg import Pool, PostgresError, DataError
from loguru import logger
from config import DEFUALT_IMG
from utils import mappers as utils
user_router = Router()


class SearchState(StatesGroup):
    waiting_for_tag = State()


class BalanceChange(StatesGroup):
    amount = State()


@user_router.message(Command("start"))
async def cmd_start(message: Message, pool: Pool) -> None:
    if message.from_user:
        username = message.from_user.username or "user"
    else:
        username = "user"
    text = (
        f"👋 <b>Hello, {username}!</b> Welcome to our Next-Gen Digital Store Bot.\n\n"
        "This bot is a fully automated e-commerce platform designed to give you "
        "a seamless shopping experience right inside Telegram.\n\n"
        "🛠️ <b>What this bot can do:</b>\n"
        "• <b>Browse & Discover:</b> Explore our structured product catalog with up-to-date pricing.\n"
        "• <b>Smart Search:</b> Find specific items instantly using our tag-based search system.\n"
        "• <b>Shopping Cart:</b> Add multiple products to your cart, manage quantities, and review your order.\n"
        "• <b>Instant Checkout:</b> Complete your purchases securely via official Telegram Stars integration.\n\n"
        "⭐️ <b>Currency & Payments:</b>\n"
        "Please note that all transactions are handled <b>exclusively using Telegram Stars (⭐️)</b>. "
        "You can easily top up your balance and start shopping right away.\n\n"
        "💡 <b>Get Started:</b> Type /catalog to explore products or /help if you need assistance."
    )
    await service.add_user(pool, message.chat.id, username)
    await message.reply(text=text, parse_mode="HTML", reply_markup=ukb.catalog)
    logger.info(f"👤 New user started: {message.chat.id} (@{username})")


@user_router.message(Command("help"))
async def help_handler(message: Message) -> None:
    help_text = (
        "🤖 <b>Welcome to the Bot Support Menu</b>\n\n"
        "Here is the list of available commands and their functions:\n\n"
        "🔹 /catalog — Browse the store catalog and view available products.\n"
        "🔹 /my_cart — View your shopping cart, manage items, and proceed to checkout.\n"
        "🔹 /search_by_tag — Find products quickly by entering specific tags.\n"
        "🔹 /my_profile — Check your user profile details, including status, balance, and inventory.\n"
        "🔹 /top_up — Add funds to your bot balance using Telegram Stars.\n"
        "🔹 /help — Display this help message with command descriptions.\n\n"
        "🛒 <b>How the Shopping Cart works:</b>\n"
        "You can explore the catalog, find the items you like, and add them to your cart. "
        "Once you are done shopping, navigate to your cart to review your order and complete the purchase.\n\n"
        "⚠️ <b>Important Payment Notice:</b>\n"
        "This bot operates <b>exclusively</b> with <b>Telegram Stars (⭐️)</b>. No other currencies or payment methods are accepted. "
        "Use the /top_up command to add stars to your balance before buying."
    )

    await message.answer(help_text, parse_mode="HTML")
    logger.debug(f"ℹ️ Help shown to {message.chat.id}")


@user_router.message(Command("my_profile"))
async def my_profile(message: Message, pool: Pool) -> None:
    chat_id = message.chat.id
    try:
        profile = await service.my_profile(pool, chat_id)
    except (PostgresError, DataError) as e:
        logger.error(f"❌ {e}", exc_info=True)
        await message.answer("❌ Database error. Please try again later.")
        return

    if not profile:
        await message.answer("❌ Profile not found. Please type /start.")
        return

    username = profile["username"]
    is_admin = bool(profile["is_admin"])
    status_label = "👑 Administrator" if is_admin else "👤 Regular User"

    balance = int(profile["balance"]) if profile["balance"] is not None else 0
    inventory = profile["inventory"] or "• No items purchased yet"

    if isinstance(inventory,list):
        inventory = utils.list_to_str(inventory,parse_mode="HTMl")

    text = f"""👤 <b>USER PROFILE</b>
━━━━━━━━━━━━━━━━━━━

🔹 <b>Account Details:</b>
• *Username:* @{username}
• *Account Status:* {status_label}

💳 <b>Financials:</b>
• *Current Balance:* {balance} ⭐️ (Telegram Stars)

📦 <b>Your Digital Inventory:</b>
{inventory}

━━━━━━━━━━━━━━━━━━━
💡 <b>Tip:</b> Use /catalog to buy more items or /top_up to add stars to your balance."""

    await message.answer(text=text, parse_mode="HTML")
    logger.info(f"👤 Profile viewed: {chat_id}, balance={balance}")


@user_router.message(Command("search_by_tag"))
async def start_tag_search(message: Message, state: FSMContext):
    await message.answer("🔍 Enter the tag you want to search for (e.g., laptop, crypto, apple):")
    await state.set_state(SearchState.waiting_for_tag)


@user_router.message(SearchState.waiting_for_tag)
async def process_tag_search(message: Message, state: FSMContext, pool: Pool):
    chat_id = message.chat.id
    tags = message.text
    if not tags:
        await message.answer("❌ Invalid tag. Please try again.")
        return

    try:
        product_names = await service.search_by_tags(pool, tags)
    except (PostgresError, DataError) as e:
        logger.error(f"❌ {e}", exc_info=True)
        await message.answer("❌ Database error. Please try again later.")
        await state.clear()
        return

    if not product_names:
        await message.answer(f"🔍 No products found with tag #{tags}.")
        await state.clear()
        return

    for row in product_names:
        name = row if isinstance(row, str) else row.get("name", "")
        product_info = await service.get_product(pool, name)
        in_cart = await service.check_user_cart(pool, chat_id, name)
        if product_info and not in_cart:
            await message.answer_photo(
                photo=product_info.get("photo_id", DEFUALT_IMG),
                caption=(
                    f"📦 <b>{name}</b>\n"
                    f"{product_info.get('description', 'is cool product')}\n"
                    f"💰 <b>price:</b> ${product_info['price']} ⭐️\n"
                    f"{product_info.get('tags', 'home')}"
                ),
                parse_mode="HTML",
                reply_markup=ukb.add_product_kb(name),
            )
    await state.clear()
    logger.info(f"🔍 Search by tag '{tags}' for {chat_id}: {len(product_names)} results")


@user_router.message(Command("catalog"))
async def cmd_catalog(message: Message) -> None:
    text = "📋 CATALOG"
    await message.reply(text=text, reply_markup=ukb.tables)
    logger.debug(f"📋 Catalog opened by {message.chat.id}")


@user_router.callback_query(F.data == "tables")
async def cmd_show(callback: CallbackQuery, pool: Pool) -> None:
    chat_id = callback.from_user.id
    try:
        product_names = await service.get_product_names(pool)
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await callback.message.answer("❌ Database error. Please try again later.")
        await callback.answer()
        return

    await callback.message.delete()
    for name in product_names:
        product_info = await service.get_product(pool, name)
        in_cart = await service.check_user_cart(pool, chat_id, name)
        if product_info and not in_cart:
            await callback.message.answer_photo(
                photo=product_info.get("photo_id", DEFUALT_IMG),
                caption=(
                    f"📦 <b>{name}</b>\n"
                    f"{product_info.get('description', 'is cool product')}\n"
                    f"💰 <b>price:</b> ${product_info['price']} ⭐️\n"
                    f"{product_info.get('tags', 'home')}"
                ),
                parse_mode="HTML",
                reply_markup=ukb.add_product_kb(name),
            )
    await callback.answer()
    logger.info(f"📋 Catalog shown to {chat_id}: {len(product_names)} products")


@user_router.callback_query(AddCart.filter())
async def add_cart(callback: CallbackQuery, callback_data: AddCart, pool: Pool) -> None:
    await callback.answer()
    product_name = callback_data.product_name
    chat_id = callback.from_user.id
    try:
        in_cart = await service.check_user_cart(pool, chat_id, product_name)
        logger.debug(f"{in_cart=}")
        if in_cart:
            await callback.message.answer(text="⚠️ This product has already been added to your cart")
            return
        await service.add_cart(pool, chat_id, product_name)
        await callback.message.delete()
        await callback.message.answer(
            text=f"✅ Added to cart: <b>{product_name}</b>", parse_mode="HTML"
        )
        logger.info(f"🛒 Cart add: {chat_id} → {product_name}")
    except (PostgresError, DataError) as e:
        logger.warning(f"⚠️ Failed to add to cart: {e}", exc_info=True)
        await callback.message.answer(text="❌ Failed to add product to cart.")
    except Exception as e:
        logger.error(f"❌ Unexpected error in add_cart: {e}", exc_info=True)
        await callback.message.answer(text="❌ An unexpected error occurred.")


@user_router.message(Command("my_cart"))
async def show_cart(message: Message, pool: Pool) -> None:
    chat_id = message.chat.id
    try:
        product_names = await service.show_names_cart(pool, chat_id)
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await message.answer("❌ Database error. Please try again later.")
        return

    if not product_names:
        await message.answer("🛒 Your cart is empty")
        return

    total_price = 0
    for name in product_names:
        product_info = await service.get_product(pool, name)
        in_cart = await service.check_user_cart(pool, chat_id, name)
        if product_info and in_cart:
            await message.answer_photo(
                photo=product_info.get("photo_id", DEFUALT_IMG),
                caption=(
                    f"📦 <b>{name}</b>\n"
                    f"{product_info.get('description', 'is cool product')}\n"
                    f"💰 <b>price:</b> ${product_info['price']} ⭐️\n"
                    f"{product_info.get('tags', 'home')}"
                ),
                parse_mode="HTML",
                reply_markup=ukb.del_product_kb(name),
            )
            total_price += int(product_info["price"])

    balance = await service.show_balance(pool, chat_id)
    balance = balance if balance is not None else 0
    text = f"🛒 Total: {total_price} ⭐️\n💰 Your balance: {balance} ⭐️"
    await message.answer(text=text, reply_markup=ukb.buy_kb)
    logger.info(f"🛒 Cart viewed: {chat_id}, total={total_price}, balance={balance}")


@user_router.callback_query(DelCart.filter())
async def del_cart(callback: CallbackQuery, callback_data: DelCart, pool: Pool) -> None:
    await callback.answer()
    chat_id = callback.from_user.id
    product_name = callback_data.product_name
    try:
        check = await service.del_product_cart(pool, chat_id, product_name)
    except PostgresError as e:
        logger.error(f"❌ {e}", exc_info=True)
        await callback.message.answer("❌ Database error. Please try again later.")
        return

    if not check:
        await callback.message.answer("⚠️ Product not found in your cart")
        return
    await callback.message.delete()
    text = f"🗑️ Removed <b>{product_name}</b> from the cart"
    await callback.message.answer(text, parse_mode="HTML")
    logger.info(f"🗑️ Cart delete: {chat_id} → {product_name}")


@user_router.message(Command("top_up"))
async def buy_answer_cmd(message: Message, pool: Pool) -> None:
    chat_id = message.chat.id

    balance = await service.show_balance(pool, chat_id)
    if balance is None:
        await message.answer("❌ Your balance is empty")
        logger.error(f"❌ {chat_id}: balance is None", exc_info=True)
        return

    total_price = await service.show_total_price(pool, chat_id)
    if total_price is None:
        await message.answer("❌ Your cart is empty")
        return

    text = f"❓ Are you sure?\n💰 Your balance: {balance} ⭐️\n🛒 Total price: {total_price} ⭐️"
    await message.delete()
    await message.answer(text=text, reply_markup=ukb.yes_or_no_buy_kb)


@user_router.callback_query(F.data == "buy:answer")
async def buy_answer(callback: CallbackQuery, pool: Pool) -> None:
    await callback.answer()
    chat_id = callback.from_user.id

    balance = await service.show_balance(pool, chat_id)
    if balance is None:
        await callback.message.answer("❌ Your balance is empty")
        logger.error(f"❌ {chat_id}: balance is None", exc_info=True)
        return

    total_price = await service.show_total_price(pool, chat_id)
    if total_price is None:
        await callback.message.answer("❌ Your cart is empty")
        return

    text = f"❓ Are you sure?\n💰 Your balance: {balance} ⭐️\n🛒 Total price: {total_price} ⭐️"
    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=ukb.yes_or_no_buy_kb)


@user_router.callback_query(F.data == "no:buy")
async def no_buy(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("✅ OK")
    logger.info(f"❌ Purchase cancelled: {callback.from_user.id}")


@user_router.callback_query(F.data == "yes:buy")
async def yes_buy(callback: CallbackQuery, pool: Pool) -> None:
    await callback.answer()
    await callback.message.delete()

    chat_id = callback.from_user.id

    names = await service.show_names_cart(pool, chat_id)
    if not names:
        await callback.message.answer("❌ Your cart is empty")
        return

    balance = await service.show_balance(pool, chat_id)
    if balance is None:
        await callback.message.answer("❌ Your balance is empty")
        logger.error(f"❌ {chat_id}: balance is None", exc_info=True)
        return

    total_price = await service.show_total_price(pool, chat_id)
    if total_price is None:
        await callback.message.answer("❌ Your cart is empty")
        return

    if total_price > balance:
        text = "❌ The total price exceeds your balance. Please top up first."
        await callback.message.answer(text=text, reply_markup=ukb.top_up_answer_kb)
        return

    try:
        await service.buy_product(pool, chat_id, names, total_price)
    except (PostgresError, DataError, Exception) as e:
        text = "❌ The transaction did not go through. Please try again."
        await callback.message.answer(text=text)
        logger.warning(f"⚠️ Buy transaction failed: {e}", exc_info=True)
        return

    new_balance = balance - total_price
    names_str = utils.list_to_str(names,parse_mode="HTML")
    text = (
        f"✅ Purchase successful! You received: <b>{names_str}</b>\n"
        f"💰 Your new balance: ⭐️<b>{new_balance}</b>"
    )
    await callback.message.answer(text=text, parse_mode="HTML")
    logger.success(f"✅ Purchase completed: {chat_id}, total={total_price}, new_balance={new_balance}")


@user_router.callback_query(F.data == "topup:answer")
async def top_up_answer(callback: CallbackQuery, pool) -> None:
    chat_id = callback.from_user.id
    balance = await service.show_balance(pool, chat_id)
    if balance is None:
        await callback.message.answer("❌ Your balance is empty")
        logger.error(f"❌ {chat_id}: balance is None", exc_info=True)
        return
    text = f"⭐️ Top up your account. Are you sure?\n💰 Your balance: {balance} ⭐️"
    await callback.message.delete()
    await callback.message.answer(text=text, reply_markup=ukb.yes_or_no_top_up_kb)


@user_router.callback_query(F.data == "no:topup")
async def no_top_up(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("✅ OK")


@user_router.callback_query(F.data == "yes:topup")
async def yes_top_up(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await callback.message.delete()
    text = "⭐️ Enter the amount you want to add to your account:"
    await callback.message.answer(text=text)
    await state.set_state(BalanceChange.amount)


@user_router.message(BalanceChange.amount)
async def set_amount(message: Message, state: FSMContext, pool: Pool) -> None:
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("❌ The amount must be greater than zero")
            return
    except (ValueError, TypeError) as e:
        await message.answer("❌ Invalid amount. Please enter a valid number.")
        logger.warning(f"⚠️ Amount not int: {e}", exc_info=True)
        return

    await state.update_data(amount=amount)
    prices = [LabeledPrice(label="⭐️ Top up balance", amount=amount)]

    try:
        await message.answer_invoice(
            title="⭐️ Top Up",
            description="Account top-up with Telegram Stars",
            prices=prices,
            provider_token="",
            payload="top_up",
            currency="XTR",
        )
        await state.clear()
        logger.info(f"⭐️ Invoice sent for top-up: {message.chat.id}, amount={amount}")
    except TelegramBadRequest as e:
        logger.error(f"❌ Invalid invoice parameters: {e}", exc_info=True)
        await message.answer("❌ An error occurred while generating the invoice. Please contact support.")
    except TelegramAPIError as e:
        logger.error(f"❌ Telegram API error while sending invoice: {e}", exc_info=True)
        await message.answer("❌ Payment service is temporarily unavailable. Please try again later.")


@user_router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)
    logger.debug(f"✅ Pre-checkout approved: {pre_checkout_query.from_user.id}")


@user_router.message(F.successful_payment)
async def success_payment_handler(message: Message, pool: Pool):
    payment_info = message.successful_payment
    chat_id = message.chat.id
    stars_amount = payment_info.total_amount

    balance = await service.show_balance(pool, chat_id)
    if balance is None:
        await message.answer("❌ Your balance is empty")
        logger.error(f"❌ {chat_id}: balance is None after payment", exc_info=True)
        return

    try:
        await service.change_balance(pool, chat_id, balance, stars_amount)
        await message.answer(
            f"✅ Thank you for your payment! "
            f"Amount charged: {stars_amount} ⭐️"
        )
        logger.success(f"⭐️ Top-up successful: {chat_id}, amount={stars_amount}, "
                       f"balance_before={balance}")
    except (PostgresError, DataError, ValueError) as e:
        logger.critical(f"❌ Failed to update balance after payment: {e}", exc_info=True)
        await message.answer("❌ Payment was processed but balance update failed. Contact support.")
