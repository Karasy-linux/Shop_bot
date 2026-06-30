from database import service 
from keyboards import user_kb as ukb
from keyboards.user_kb import AddCart, DelCart
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, LabeledPrice, PreCheckoutQuery
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from asyncpg import Pool
from loguru import logger
from config import DEFUALT_IMG

user_router = Router()


class SearchState(StatesGroup):
    waiting_for_tag = State()

class BalanceChange(StatesGroup):
    amount = State()


@user_router.message(Command("start"))
async def cmd_start(message: Message,pool: Pool) -> None:
    if message.from_user:
        username = message.from_user.username or "user"
    else:
        username = "user"
    text = (
        f"👋 *Hello, {username}!* Welcome to our Next-Gen Digital Store Bot.\n\n"
        "This bot is a fully automated e-commerce platform designed to give you "
        "a seamless shopping experience right inside Telegram.\n\n"
        "🛠️ *What this bot can do:*\n"
        "• *Browse & Discover:* Explore our structured product catalog with up-to-date pricing.\n"
        "• *Smart Search:* Find specific items instantly using our tag-based search system.\n"
        "• *Shopping Cart:* Add multiple products to your cart, manage quantities, and review your order.\n"
        "• *Instant Checkout:* Complete your purchases securely via official Telegram Stars integration.\n\n"
        "⭐️ *Currency & Payments:*\n"
        "Please note that all transactions are handled **exclusively using Telegram Stars (⭐️)**. "
        "You can easily top up your balance and start shopping right away.\n\n"
        "💡 *Get Started:* Type /catalog to explore products or /help if you need assistance."
    )
    await message.answer(text, parse_mode="Markdown")
    await service.add_user(pool,message.chat.id,username)
    await message.reply(text=text,reply_markup=ukb.catalog)


@user_router.message(Command("help"))
async def help_handler(message: Message) -> None:
    help_text = (
        "🤖 *Welcome to the Bot Support Menu*\n\n"
        "Here is the list of available commands and their functions:\n\n"
        "🔹 /catalog — Browse the store catalog and view available products.\n"
        "🔹 /my_cart — View your shopping cart, manage items, and proceed to checkout.\n"
        "🔹 /search_by_tag — Find products quickly by entering specific tags.\n"
        "🔹 /top_up — Add funds to your bot balance using Telegram Stars.\n"
        "🔹 /help — Display this help message with command descriptions.\n\n"
        "🛒 *How the Shopping Cart works:*\n"
        "You can explore the catalog, find the items you like, and add them to your cart. "
        "Once you are done shopping, navigate to your cart to review your order and complete the purchase.\n\n"
        "⚠️ *Important Payment Notice:*\n"
        "This bot operates **exclusively** with **Telegram Stars (⭐️)**. No other currencies or payment methods are accepted. "
        "Use the /top_up command to add stars to your balance before buying."
    )
    
    await message.answer(help_text, parse_mode="Markdown")


@user_router.message(Command("search_by_tag"))
async def start_tag_search(message: Message, state: FSMContext):
    await message.answer("Enter the tag you want to search for (e.g., laptop, crypto, apple):")
    await state.set_state(SearchState.waiting_for_tag)


@user_router.message(SearchState.waiting_for_tag)
async def process_tag_search(message:Message, state:FSMContext, pool:Pool):
    chat_id = message.chat.id
    tags = message.text
    if not tags:
        await message.answer("Invalid tag. Please try again.")
        return

    product_names = await service.search_by_tags(pool,tags)

    if not product_names:
        await message.answer(f"No products found with tag #{tags}.")
        await state.clear()
        return

    for name in product_names:
        product_info = await service.get_product(pool, name)
        in_cart = await service.check_user_cart(pool,chat_id,name)
    if product_info and not in_cart:
        await message.answer_photo(
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
    await state.clear()


@user_router.message(Command("catalog"))
async def cmd_catalog(message: Message) -> None:
    text = "CATALOG"
    await message.reply(text=text,reply_markup=ukb.tables)


@user_router.callback_query(F.data == "tables")
async def cmd_show(callback: CallbackQuery, pool: Pool) -> None:
    product_names = await service.get_product_names(pool)
    chat_id = callback.from_user.id

    await callback.message.delete()
    for name in product_names:
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
    rows = await service.show_names_cart(pool,chat_id)
    if not rows:
        await message.answer("You do not have a products in the cart")
        return
    product_names = [row['name'] for row in rows]

    for name in product_names:
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


@user_router.message(Command("top_up"))
async def buy_answer_cmd(message:Message, pool:Pool) -> None:
    chat_id = message.chat.id

    if balance := await service.show_balance(pool,chat_id) is None:
        await message.answer("Your balance is empty")
        logger.error(f"{balance=}. However, balance must is not None",exc_info=True)
        return
    if total_price := await service.show_total_price(pool,chat_id) is None:
        await message.answer("Your cart is empty")
        return
    text = f"YOU SHURE? \n Your balance:{balance} \n total price:{total_price}"
    await message.delete()
    await message.answer(text=text,reply_markup=ukb.yes_or_no_buy_kb)


@user_router.callback_query(F.data == "buy:answer")
async def buy_answer(callback: CallbackQuery, pool:Pool) -> None:
    await callback.answer()
    chat_id = callback.from_user.id

    if balance := await service.show_balance(pool,chat_id) is None:
        await callback.message.answer("Your balance is empty")
        logger.error(f"{balance=}. However, balance must is not None",exc_info=True)
        return
    if total_price := await service.show_total_price(pool,chat_id) is None:
        await callback.message.answer("Your cart is empty")
        return
    text = f"YOU SHURE? \n Your balance:{balance} \n total price:{total_price}"
    await callback.message.delete()
    await callback.message.answer(text=text,reply_markup=ukb.yes_or_no_buy_kb)


@user_router.callback_query(F.data == "no:buy")
async def no_buy(callback:CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("OK")


@user_router.callback_query(F.data == "yes:buy")
async def yes_buy(callback:CallbackQuery, pool:Pool) -> None:
    await callback.answer()
    await callback.message.delete()

    chat_id = callback.from_user.id
    if names := await service.show_names_cart(pool,chat_id):
        await callback.message.answer("Your cart is empty")
        return
    if balance := await service.show_balance(pool,chat_id) is None:
        await callback.message.answer("Your balance is empty")
        logger.error(f"{balance=}. However, balance must is not None",exc_info=True)
        return
    if total_price := await service.show_total_price(pool,chat_id) is None:
        await callback.message.answer("Your cart is empty")
        return
    if total_price > balance:
        text = "The total price exceeds your balance"
        await callback.message.answer(text=text,reply_markup=ukb.top_up_answer_kb)

    try:
        await service.buy_product(pool,chat_id,names,total_price,balance)
        await service.change_balance(pool,chat_id,balance,total_price)
    except ValueError as e:
        text = "The transaction did not go through"
        await callback.message.answer(text=text)
        logger.warning(f"{e}",exc_info=True)
        return
    
    new_balance = balance - total_price
    inventory = await service.show_inventory(pool,chat_id)
    text = (f"Success operetion you got the *{inventory}*" 
            f"Now your balance: *{new_balance}*")
    await callback.message.answer(text=text,parse_mode="MarkdownV2")


@user_router.callback_query(F.data == "topup:answer")
async def top_up_answer(callback:CallbackQuery) -> None:
    chat_id = callback.from_user.id

    if balance := await service.show_balance(pool,chat_id) is None:
        await callback.message.answer("Your balance is empty")
        logger.error(f"{balance=}. However, balance must is not None",exc_info=True)
        return
    text = f"Top up your accaunt. YOU SHURE?  \n Your balance:{balance}"
    await callback.message.delete()
    await callback.message.answer(text=text,reply_markup=ukb.yes_or_no_top_up_kb)


@user_router.callback_query(F.data == "no:topup")
async def no_top_up(callback:CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()
    await callback.message.answer("OK")


@user_router.callback_query(F.data == "yes:topup")
async def yes_top_up(callback:CallbackQuery, state:FSMContext) -> None:
    await callback.answer()
    await callback.message.delete()
    text = "⭐️Enter the amount you want to add to your account⭐️"
    await callback.message.answer(text=text)
    await state.set_state(BalanceChange.amount)


@user_router.message(BalanceChange.amount)
async def set_amount(message:Message, state:FSMContext, pool:Pool) -> None:
    try:
        amount = int(message.text)
        if amount <= 0:
            await message.answer("The amount must be greater than zero")
            return
    except ValueError as e:
        await message.answer("Invalid amount. Please enter a valid number")
        logger.warning(f"amount not int {e}",exc_info=True)
        return
    await state.update_data(amount=amount)

    prices = [LabeledPrice(label="Преміум статус", amount=amount)]

    try:
        await message.answer_invoice(
        title="top up",
        description="account top-up",
        prices=prices,
        provider_token="", 
        payload="top_up",
        currency="XTR" 
    )
        await state.clear()
    except TelegramBadRequest as e:
        logger.error(f"Invalid invoice parameters: {e}", exc_info=True)
        await message.answer("An error occurred while generating the invoice. Please contact support.")
        return
    
    except TelegramAPIError as e:
        logger.error(f"Telegram API error while sending invoice: {e}", exc_info=True)
        await message.answer("The payment service is temporarily unavailable. Please try again in a minute.")
        return 
    
@user_router.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@user_router.message(F.successful_payment)
async def success_payment_handler(message: Message, pool: Pool):
    payment_info = message.successful_payment
    chat_id = message.chat.id
    payload = payment_info.invoice_payload
    stars_amount = payment_info.total_amount 
    if balance := await service.show_balance(pool,chat_id) is None:
        await message.answer("Your balance is empty")
        logger.error(f"{balance=}. However, balance must is not None",exc_info=True)
        return
    try:
        await service.change_balance(pool,chat_id,balance,payload) 
        await message.answer(f"Thank you for your payment! Your order has been processed. Amount charged: {stars_amount} ⭐️")
    except ValueError as e:
        logger.critical(f"{e}",exc_info=True)