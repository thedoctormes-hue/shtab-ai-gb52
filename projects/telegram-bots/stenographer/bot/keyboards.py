from aiogram.types import InlineKeyboardMarkup

def get_protocol_keyboard() -> InlineKeyboardMarkup:
    # Кнопки убраны — магия без выбора!
    return InlineKeyboardMarkup(inline_keyboard=[])