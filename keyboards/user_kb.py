from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


class AddCart(CallbackData, prefix="add_cart"):
    product_name: str


class DelCart(CallbackData, prefix="del_cart"):
    product_name: str


def add_product_kb(product_name: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🛒 Add to cart",
        callback_data=AddCart(product_name=product_name),
    )
    return builder.as_markup()


def del_product_kb(product_name: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🗑️ Delete from cart",
        callback_data=DelCart(product_name=product_name),
    )
    return builder.as_markup()


reply_builder = ReplyKeyboardBuilder()
reply_builder.add(KeyboardButton(text="/catalog"))
reply_builder.add(KeyboardButton(text="/my_cart"))
reply_builder.add(KeyboardButton(text="/search_by_tag"))
reply_builder.add(KeyboardButton(text="/top_up"))
reply_builder.add(KeyboardButton(text="/help"))
reply_builder.add(KeyboardButton(text="/my_profile"))
catalog = reply_builder.as_markup(resize_keyboard=True)


inline_builder = InlineKeyboardBuilder()
inline_builder.add(InlineKeyboardButton(text="📋 Catalog", callback_data="tables"))
tables = inline_builder.as_markup()

product = InlineKeyboardBuilder()
product.add(InlineKeyboardButton(text="🛒 Add to cart", callback_data="add:cart"))
product_kb = product.as_markup()


buy_answer = InlineKeyboardBuilder()
buy_answer.add(InlineKeyboardButton(text="💳 Buy", callback_data="buy:answer"))
buy_kb = buy_answer.as_markup()

yes_or_no_buy = InlineKeyboardBuilder()
yes_or_no_buy.add(InlineKeyboardButton(text="✅ YES", callback_data="yes:buy"))
yes_or_no_buy.add(InlineKeyboardButton(text="❌ NO", callback_data="no:buy"))
yes_or_no_buy_kb = yes_or_no_buy.as_markup()


top_up_answer = InlineKeyboardBuilder()
top_up_answer.add(InlineKeyboardButton(text="⭐️ Top up", callback_data="topup:answer"))
top_up_answer_kb = top_up_answer.as_markup()

yes_or_no_top_up = InlineKeyboardBuilder()
yes_or_no_top_up.add(InlineKeyboardButton(text="✅ YES", callback_data="yes:topup"))
yes_or_no_top_up.add(InlineKeyboardButton(text="❌ NO", callback_data="no:topup"))
yes_or_no_top_up_kb = yes_or_no_top_up.as_markup()
