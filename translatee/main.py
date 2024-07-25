import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from database import init_db, add_user, get_all_users
from buttons.inline import get_language_keyboard, languages_dict

API_TOKEN = '7231442870:AAGfupxHgK6-_YnhklkZh_lMIAgLi5ixCn0'
API_URL = 'https://cvt.su/x/translator/?from=auto&to={}&text={}'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

ADMIN_PASSWORD = '08080'

class AdminState(StatesGroup):
    waiting_for_password = State()

async def translate_text(text: str, to_lang: str) -> str:
    url = API_URL.format(to_lang, text)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('result', 'Translation failed')
            else:
                return 'API request failed'

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    
    add_user(user_id, username, full_name)
    
    await message.answer(f"Salom hurmatli <b>{full_name}</b> 👋\n\nTarjimon botimizga xushkelibsiz.\nBotimizdan bemalol foydalanishingiz mumkin!!!")
    await message.answer("Tarjima qilishingiz kerak bo'lgan matningizni kiriting 👇")

@dp.message_handler(commands=["admin"])
async def admin_handler(message: types.Message):
    await message.answer("Iltimos, parolni kiriting:")
    await AdminState.waiting_for_password.set()

@dp.message_handler(state=AdminState.waiting_for_password)
async def password_handler(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        users_button = InlineKeyboardButton("Users", callback_data="list_users")
        keyboard = InlineKeyboardMarkup().add(users_button)
        await message.answer("Xush kelibsiz admin!", reply_markup=keyboard)
    else:
        await message.answer("Noto'g'ri parol!")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "list_users")
async def list_users_handler(callback_query: types.CallbackQuery):
    users = get_all_users()
    users_list = "\n".join([f"{user[2]} (@{user[1]})" for user in users])
    if users_list:
        await bot.send_message(callback_query.from_user.id, f"Botdan foydalanayotgan foydalanuvchilar:\n\n{users_list}")
    else:
        await bot.send_message(callback_query.from_user.id, "Hech qanday foydalanuvchi yo'q.")
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler()
async def handle_message(message: types.Message):
    text = message.text
    lang_code = 'uz'
    translated_text = await translate_text(text, lang_code)
    await message.answer(f"<code>{translated_text}</code>", parse_mode='HTML', reply_markup=get_language_keyboard(1))

@dp.callback_query_handler(lambda c: c.data.startswith('page_'))
async def handle_pagination(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=get_language_keyboard(page))

@dp.callback_query_handler(lambda c: c.data in languages_dict.keys())
async def translate_text_handler(call: types.CallbackQuery):
    lang_code = call.data
    text = call.message.text
    translated_text = await translate_text(text, lang_code)
    await call.message.edit_text(f"<code>{translated_text}</code>", parse_mode='HTML', reply_markup=get_language_keyboard(1))
    await bot.answer_callback_query(call.id)

async def on_start_up(dp):
    await bot.send_message(chat_id=1921911753, text='Bot ishga tushdi!')

async def on_shutdown(dp):
    await bot.send_message(chat_id=1921911753, text='Bot o\'chdi!')

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up, on_shutdown=on_shutdown)
