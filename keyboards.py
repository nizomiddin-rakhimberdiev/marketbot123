from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import Database

db = Database()

def admin_btns():
    kbs = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Add product"),
                KeyboardButton(text="Get products"),
            ]
        ], resize_keyboard=True
    )
    return kbs


def students_btns():
    students = db.get_students()
    kb = InlineKeyboardBuilder()
    for s in students:
        kb.button(text=s[3], callback_data=f"student_{s[0]}") 
    kb.adjust(3) # nechi qatorligi belgilaydi
    return kb.as_markup()

def products_btns():
    products = db.get_products()
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=p[1], callback_data=f"product_{p[0]}") 
    kb.adjust(3) # nechi qatorligi belgilaydi
    return kb.as_markup()

def users_btn():
    kbs = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Menu'),
                KeyboardButton(text='Buyurtmalarim'),
            ],
            [
                KeyboardButton(text='Savatcha'),
            ],
        ],
        resize_keyboard=True
    )
    return kbs

def plus_minus_btns(product_id, count=1):
    kb = InlineKeyboardBuilder()
    kb.button(text="-", callback_data=f"minus_{product_id}")
    kb.button(text=f"{count}", callback_data=f"count_{product_id}")
    kb.button(text="+", callback_data=f"plus_{product_id}")
    kb.button(text="Savatchaga qo'shish", callback_data=f"add_to_cart_{product_id}")
    kb.adjust(3)
    return kb.as_markup()