from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, \
    KeyboardButton
# from . import const
from app import const


def get_buttons(buttons, n=2):
    rkm = ReplyKeyboardMarkup(True, row_width=n)
    rkm.add(*(KeyboardButton(btn) for btn in buttons))
    return rkm


def get_main_menu_keyboard():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    rkm.add(*(KeyboardButton(btn) for btn in const.MAIN_MENU_KEYBOARD))
    return rkm


def remove_kb():
    return ReplyKeyboardRemove()


count_buttons = [
    '1', '2', '3', 'Backspace',
    '4', '5', '6', 'C',
    '7', '8', '9', '-',
    '00', '0', '.', 'OK'
]


def get_product_amount_btns():
    rkm = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    rkm.add(*(KeyboardButton(btn) for btn in count_buttons))
    return rkm
