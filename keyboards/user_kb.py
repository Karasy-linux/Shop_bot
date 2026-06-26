from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

class AddCart(CallbackData,prefix="add_cart"):
    product_name: str

class DelCart(CallbackData,prefix="del_cart"):
    product_name: str


def add_product_kb(product_name: str):
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🛒 add to cart", 
        callback_data=AddCart(product_name=product_name)
    )
    return builder.as_markup()

def del_product_kb(product_name: str):
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🛒 delete from cart", 
        callback_data=DelCart(product_name=product_name)
    )
    return builder.as_markup()


reply_builder = ReplyKeyboardBuilder()
reply_builder.add(KeyboardButton(text="/catalog"))
catalog = reply_builder.as_markup(resize_keyboard=True)


inline_builder = InlineKeyboardBuilder()
inline_builder.add(InlineKeyboardButton(text="tables",callback_data="tables"))
tables = inline_builder.as_markup()

product = InlineKeyboardBuilder()
product.add(InlineKeyboardButton(text="add to cart",callback_data="add:cart"))
product_kb = product.as_markup()