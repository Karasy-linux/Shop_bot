from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

reply_builder = ReplyKeyboardBuilder()

reply_builder.add(KeyboardButton(text="/catalog"))
catalog = reply_builder.as_markup(resize_keyboard=True)


inline_builder = InlineKeyboardBuilder()

inline_builder.add(InlineKeyboardButton(text="tables",callback_data="tables"))
tables = inline_builder.as_markup()

