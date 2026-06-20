from operator import add

from aiogram.types import KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



tables_builder = InlineKeyboardBuilder()

tables_builder.add(InlineKeyboardButton(text="add a product",callback_data="add:product"))
tables_builder.add(InlineKeyboardButton(text="edit a product",callback_data="edit:product"))
tables_builder.add(InlineKeyboardButton(text="delete a product",callback_data="delete:product"))
tables = tables_builder.as_markup()


#___________________________________
#________add:product________________
#___________________________________



add_name = InlineKeyboardBuilder()
add_name.add(InlineKeyboardButton(text="set name",callback_data="set:name"))
add_name.add(InlineKeyboardButton(text="cancel",callback_data="set:cancel"))
add_name_kb = add_name.as_markup()

add_price = InlineKeyboardBuilder()
add_price.add(InlineKeyboardButton(text="set price",callback_data="set:price"))
add_price.add(InlineKeyboardButton(text="cancel",callback_data="set:cancel"))
add_price_kb = add_price.as_markup()

add_tags = InlineKeyboardBuilder()
add_tags.add(InlineKeyboardButton(text="set tags",callback_data="set:tags"))
add_tags.add(InlineKeyboardButton(text="cancel",callback_data="set:cancel"))
add_tags_kb = add_tags.as_markup()

add_description = InlineKeyboardBuilder()
add_description.add(InlineKeyboardButton(text="set description",callback_data="set:description"))
add_description.add(InlineKeyboardButton(text="cancel",callback_data="set:cancel"))
add_description.add(InlineKeyboardButton(text="skip",callback_data="set:skip"))
add_description_kb = add_description.as_markup()

add_photo = InlineKeyboardBuilder()
add_photo.add(InlineKeyboardButton(text="set photo",callback_data="set:photo"))
add_photo.add(InlineKeyboardButton(text="cancel",callback_data="set:cancel"))
add_photo.add(InlineKeyboardButton(text="skip",callback_data="set:finish"))
add_photo_kb = add_photo.as_markup()


add_finally = InlineKeyboardBuilder()
add_finally.add(InlineKeyboardButton(text="cancel",callback_data="set:cancel"))
add_finally.add(InlineKeyboardButton(text="finish",callback_data="set:finish"))
add_finally_kb = add_finally.as_markup()