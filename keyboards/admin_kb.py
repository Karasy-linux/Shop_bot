from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

tables_builder = InlineKeyboardBuilder()

tables_builder.add(InlineKeyboardButton(text="📦 Add product", callback_data="add:product"))
tables_builder.add(InlineKeyboardButton(text="✏️ Edit product", callback_data="edit:product"))
tables_builder.add(InlineKeyboardButton(text="🗑️ Delete product", callback_data="delete:product"))
tables = tables_builder.as_markup()


# ___________________________________
# ________add:product________________
# ___________________________________


add_name = InlineKeyboardBuilder()
add_name.add(InlineKeyboardButton(text="✏️ Set name", callback_data="set:name"))
add_name.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
add_name_kb = add_name.as_markup()

add_price = InlineKeyboardBuilder()
add_price.add(InlineKeyboardButton(text="💰 Set price", callback_data="set:price"))
add_price.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
add_price_kb = add_price.as_markup()

add_tags = InlineKeyboardBuilder()
add_tags.add(InlineKeyboardButton(text="🏷️ Set tags", callback_data="set:tags"))
add_tags.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
add_tags_kb = add_tags.as_markup()

add_description = InlineKeyboardBuilder()
add_description.add(InlineKeyboardButton(text="📝 Set description", callback_data="set:description"))
add_description.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
# add_description.add(InlineKeyboardButton(text="skip",callback_data="set:skip"))
add_description_kb = add_description.as_markup()

add_photo = InlineKeyboardBuilder()
add_photo.add(InlineKeyboardButton(text="📸 Set photo", callback_data="set:photo"))
add_photo.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
# add_photo.add(InlineKeyboardButton(text="skip and finish",callback_data="set:finish"))
add_photo_kb = add_photo.as_markup()


add_finally = InlineKeyboardBuilder()
add_finally.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
add_finally.add(InlineKeyboardButton(text="✅ Finish", callback_data="set:finish"))
add_finally_kb = add_finally.as_markup()


# _____________________________
# ___edit:product______________
# _____________________________


edit_product = InlineKeyboardBuilder()
edit_product.add(InlineKeyboardButton(text="✏️ Write name", callback_data="edit:set:product"))
edit_product.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
edit_product_kb = edit_product.as_markup()

edit_price = InlineKeyboardBuilder()
edit_price.add(InlineKeyboardButton(text="💰 Write price", callback_data="edit:price"))
edit_price.add(InlineKeyboardButton(text="⏭️ Skip", callback_data="edit:skip"))
edit_price.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
edit_price_kb = edit_price.as_markup()

edit_tags = InlineKeyboardBuilder()
edit_tags.add(InlineKeyboardButton(text="🏷️ Write tags", callback_data="edit:tags"))
edit_tags.add(InlineKeyboardButton(text="⏭️ Skip", callback_data="edit:skip"))
edit_tags.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
edit_tags_kb = edit_tags.as_markup()

edit_description = InlineKeyboardBuilder()
edit_description.add(InlineKeyboardButton(text="📝 Write description", callback_data="edit:description"))
edit_description.add(InlineKeyboardButton(text="⏭️ Skip", callback_data="edit:skip"))
edit_description.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
edit_description_kb = edit_description.as_markup()

edit_photo = InlineKeyboardBuilder()
edit_photo.add(InlineKeyboardButton(text="📸 Send photo", callback_data="edit:photo"))
edit_photo.add(InlineKeyboardButton(text="⏭️ Skip & finish", callback_data="edit:finish"))
edit_photo.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
edit_photo_kb = edit_photo.as_markup()

edit_finally = InlineKeyboardBuilder()
edit_finally.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
edit_finally.add(InlineKeyboardButton(text="✅ Finish", callback_data="edit:finish"))
edit_finally_kb = edit_finally.as_markup()


# _____________________________
# ___delete:product____________
# _____________________________

delete_product = InlineKeyboardBuilder()
delete_product.add(InlineKeyboardButton(text="✏️ Write name", callback_data="delete:set:name"))
delete_product.add(InlineKeyboardButton(text="❌ Cancel", callback_data="cancel"))
delete_product_kb = delete_product.as_markup()
