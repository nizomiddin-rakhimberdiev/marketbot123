from aiogram import Bot, Dispatcher, types, F
import asyncio
import os
from database import Database
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from keyboards import students_btns, admin_btns, products_btns, users_btn, plus_minus_btns

class RegisterState(StatesGroup):
    phone = State()

class AddProductState(StatesGroup):
    name = State()
    price = State()
    image = State()
    count = State()

db = Database()
bot = Bot(token="8616651254:AAFzw_H-TySYYSN8IUzSTPYXSD_bXfZJWEU")
dp = Dispatcher()

ADMIN_IDS = [726130790, 35823495]

@dp.message(F.text == "/start")
async def start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = db.check_user(str(user_id))
    if user:
        await message.answer("Assalomu alaykum, botga xush kelibsiz!", reply_markup=users_btn())
    else:
        await message.answer("Ro'yxatdan o'tish uchun tel raqamingizni kiriting:")
        await state.set_state(RegisterState.phone)

@dp.message(F.text == "Menu")
async def menu(message: types.Message):
    await message.answer("Maxsulotlardan birini tanlang:", reply_markup=products_btns())

@dp.callback_query(F.data.startswith('product_'))
async def product_handler(call: types.CallbackQuery):
    id = int(call.data.split('_')[1])
    product = db.get_product(id)
    if product:
        cart_item = db.get_cart_item(call.from_user.id, id)
        if cart_item:
            count = cart_item[3]
            await call.message.answer_photo(photo=product[3], caption=f"{product[1]}\nNarxi: {product[2]}\nSoni: {product[4]}", reply_markup=plus_minus_btns(product[0], count))
        else:
            await call.message.answer_photo(photo=product[3], caption=f"{product[1]}\nNarxi: {product[2]}\nSoni: {product[4]}", reply_markup=plus_minus_btns(product[0]))
    else:
        print("Bunaqa mahsulot yo'q")

@dp.callback_query(F.data.startswith('plus_'))
async def plus_handler(call: types.CallbackQuery):
    product_id = int(call.data.split('_')[1])
    count = int(call.message.reply_markup.inline_keyboard[0][1].text)
    product = db.get_product(product_id)
    if product and product[4] > count:
        count += 1
        await call.message.edit_reply_markup(reply_markup=plus_minus_btns(product_id, count))
    else:
        pass

@dp.callback_query(F.data.startswith('add_to_cart_'))
async def add_to_cart_handler(call: types.CallbackQuery):
    product_id = int(call.data.split('_')[3])
    count = int(call.message.reply_markup.inline_keyboard[0][1].text)
    user_id = call.from_user.id
    db.add_to_cart(user_id, product_id, count)
    await call.message.answer("Mahsulot savatchaga qo'shildi!")

@dp.message(F.text == "Savatcha")
async def cart(message: types.Message):
    user_id = message.from_user.id
    cart_items = db.get_cart(user_id)
    if cart_items:
        text = "Savatchangizdagi mahsulotlar:\n\n"
        total_price = 0
        for item in cart_items:
            product = db.get_product(item[2])
            text += f"{product[1]} - {item[3]} ta - Narxi: {product[2] * item[3]}\n"
            total_price += product[2] * item[3]
        text += f"\nJami narx: {total_price}"
        await message.answer(text)
    else:
        await message.answer("Savatchangiz bo'sh!")

@dp.callback_query(F.data.startswith('minus_'))
async def plus_handler(call: types.CallbackQuery):
    product_id = int(call.data.split('_')[1])
    count = int(call.message.reply_markup.inline_keyboard[0][1].text)
    if count > 1:
        count -= 1
        await call.message.edit_reply_markup(reply_markup=plus_minus_btns(product_id, count))
    else:
        pass

@dp.message(F.text == "/admin")
async def admin(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Admin paneliga xush kelibsiz!", reply_markup=admin_btns())
    else:
        pass

@dp.message(F.text == "Add product")
async def add_product(message: types.Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("Mahsulot nomini kiriting:")
        await state.set_state(AddProductState.name)

@dp.message(AddProductState.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer("Mahsulot narxini kiriting:")
    await state.set_state(AddProductState.price)

@dp.message(AddProductState.price)
async def process_price(message: types.Message, state: FSMContext):
    price = int(message.text)
    await state.update_data(price=price)
    await message.answer("Mahsulot rasm linkini kiriting:")
    await state.set_state(AddProductState.image)

@dp.message(AddProductState.image, F.photo)
async def process_image(message: types.Message, state: FSMContext):
    image = message.photo[-1].file_id
    await state.update_data(image=image)
    await message.answer("Mahsulot sonini kiriting:")
    await state.set_state(AddProductState.count)

@dp.message(AddProductState.count)
async def process_count(message: types.Message, state: FSMContext):
    count = int(message.text)
    data = await state.get_data()
    name = data['name']
    price = data['price']
    image = data['image']
    db.add_product(name, price, image, count)
    await message.answer("Mahsulot muvaffaqiyatli qo'shildi!")
    await state.clear()

@dp.message(F.text == "Get products")
async def get_products(message: types.Message):
    await message.answer("Mahsulotlardan birini tanlang", reply_markup=products_btns())

@dp.callback_query(F.data.startswith('product_'))
async def product_handler(call: types.CallbackQuery):
    id = int(call.data.split('_')[1])
    product = db.get_product(id)
    if product:
        await call.message.answer_photo(photo=product[3], caption=f"{product[1]}\nNarxi: {product[2]}\nSoni: {product[4]}")
    else:
        print("Bunaqa mahsulot yo'q")


@dp.message(RegisterState.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    full_name = message.from_user.full_name
    user_id = message.from_user.id
    db.add_user(str(user_id), phone, full_name)
    await message.answer("Ro'yxatdan muvaffaqiyatli o'tdingiz!")
    await state.clear()



@dp.message(F.text=='/students')
async def students_handler(message: types.Message):
    await message.answer("Student ismlaridan birini tanlang", reply_markup=students_btns())
    
@dp.callback_query(F.data.startswith('student_'))
async def student_handler(call: types.CallbackQuery):
    id = int(call.data.split('_')[1])
    student = db.get_student(id)
    if student:
        await call.message.answer(f"{student[3]}\n{student[1]}\n{student[2]}")
    else:
        print("Bunaqa student yo'q")

async def main():
    print("Бот запущен...")
    db.create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())