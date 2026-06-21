
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
add_name.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
add_name_kb = add_name.as_markup()

add_price = InlineKeyboardBuilder()
add_price.add(InlineKeyboardButton(text="set price",callback_data="set:price"))
add_price.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
add_price_kb = add_price.as_markup()

add_tags = InlineKeyboardBuilder()
add_tags.add(InlineKeyboardButton(text="set tags",callback_data="set:tags"))
add_tags.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
add_tags_kb = add_tags.as_markup()

add_description = InlineKeyboardBuilder()
add_description.add(InlineKeyboardButton(text="set description",callback_data="set:description"))
add_description.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
add_description.add(InlineKeyboardButton(text="skip",callback_data="set:skip"))
add_description_kb = add_description.as_markup()

add_photo = InlineKeyboardBuilder()
add_photo.add(InlineKeyboardButton(text="set photo",callback_data="set:photo"))
add_photo.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
add_photo.add(InlineKeyboardButton(text="skip",callback_data="set:finish"))
add_photo_kb = add_photo.as_markup()


add_finally = InlineKeyboardBuilder()
add_finally.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
add_finally.add(InlineKeyboardButton(text="finish",callback_data="set:finish"))
add_finally_kb = add_finally.as_markup()


#_____________________________
#___edit:product______________
#_____________________________


edit_product = InlineKeyboardBuilder()
edit_product.add(InlineKeyboardButton(text="write name",callback_data="edit:set:name"))
edit_product.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
edit_product_kb = edit_product.as_markup()

edit_price = InlineKeyboardBuilder()
edit_price.add(InlineKeyboardButton(text="write price",callback_data="edit:price"))
edit_price.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
edit_price.add(InlineKeyboardButton(text="skip",callback_data="edit:skip"))
edit_price_kb = edit_price.as_markup()

edit_tags = InlineKeyboardBuilder()
edit_tags.add(InlineKeyboardButton(text="write tags",callback_data="edit:tags"))
edit_tags.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
edit_tags.add(InlineKeyboardButton(text="skip",callback_data="edit:skip"))
edit_tags_kb = edit_tags.as_markup()

edit_description = InlineKeyboardBuilder()
edit_description.add(InlineKeyboardButton(text="write description",callback_data="edit:description"))
edit_description.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
edit_description.add(InlineKeyboardButton(text="skip",callback_data="edit:skip"))
edit_description_kb = edit_description.as_markup()

edit_photo = InlineKeyboardBuilder()
edit_photo.add(InlineKeyboardButton(text="write photo",callback_data="edit:photo"))
edit_photo.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
edit_photo.add(InlineKeyboardButton(text="skip",callback_data="edit:skip"))
edit_photo_kb = edit_photo.as_markup()

edit_finally = InlineKeyboardBuilder()
edit_finally.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
edit_finally.add(InlineKeyboardButton(text="finish",callback_data="edit:finish"))
edit_finally_kb = edit_finally.as_markup()


#_____________________________
#___delete:product____________
#_____________________________

delete_product = InlineKeyboardBuilder()
delete_product.add(InlineKeyboardButton(text="write name",callback_data="delete:set:name"))
delete_product.add(InlineKeyboardButton(text="cancel",callback_data="cancel"))
delete_product_kb = delete_product.as_markup()
