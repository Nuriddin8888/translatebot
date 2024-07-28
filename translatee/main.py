import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from gtts import gTTS, lang
from io import BytesIO
from database import init_db, add_user, get_all_users
from buttons.inline import get_language_keyboard, languages_dict
from state import *

API_TOKEN = '7231442870:AAGfupxHgK6-_YnhklkZh_lMIAgLi5ixCn0'
API_URL = 'https://cvt.su/x/translator/?from=auto&to={}&text={}'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

ADMIN_PASSWORD = '08080'


async def translate_text(text: str, to_lang: str) -> str:
    url = API_URL.format(to_lang, text)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('result', 'Translation failed')
            else:
                return 'API request failed'

async def text_to_speech(text: str, lang_code: str) -> BytesIO:
    tts = gTTS(text=text, lang=lang_code)
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio

async def supports_audio(lang_code: str) -> bool:
    return lang_code in lang.tts_langs()

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
        await message.answer("Assalomu aleyko'm <b>Mutalov Nuriddin</b> Xush kelibsiz!", reply_markup=keyboard)
    else:
        await message.answer("Noto'g'ri parol!")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data == "list_users")
async def list_users_handler(callback_query: types.CallbackQuery):
    users = get_all_users()
    users_list = "\n".join([f"{user[2]}  @{user[1]}" for user in users])
    if users_list:
        await bot.send_message(callback_query.from_user.id, f"Bot foydalanuvchilar:\n\n{users_list}")
    else:
        await bot.send_message(callback_query.from_user.id, "Hech qanday foydalanuvchi yo'q.")
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler()
async def handle_message(message: types.Message):
    text = message.text
    lang_code = 'uz'
    translated_text = await translate_text(text, lang_code)
    
    keyboard = get_language_keyboard(1)
    if await supports_audio(lang_code):
        audio_button = InlineKeyboardButton("Audio", callback_data=f"audio_{translated_text}_{lang_code}")
        keyboard.add(audio_button)

    await message.answer(f"<code>{translated_text}</code>", parse_mode='HTML', reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('audio_'))
async def handle_audio(callback_query: CallbackQuery):
    data = callback_query.data.split('_')
    translated_text = data[1]
    lang_code = data[2]
    audio = await text_to_speech(translated_text, lang_code)
    
    await bot.send_audio(callback_query.message.chat.id, audio, title='Translation')
    await bot.answer_callback_query(callback_query.id)

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
    
    keyboard = get_language_keyboard(1)
    if await supports_audio(lang_code):
        audio_button = InlineKeyboardButton("Audio", callback_data=f"audio_{translated_text}_{lang_code}")
        keyboard.add(audio_button)

    await call.message.edit_text(f"<code>{translated_text}</code>", parse_mode='HTML', reply_markup=keyboard)
    await bot.answer_callback_query(call.id)

async def on_start_up(dp):
    await bot.send_message(chat_id=1921911753, text='Bot ishga tushdi!')

async def on_shutdown(dp):
    await bot.send_message(chat_id=1921911753, text='Bot o\'chdi!')

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up, on_shutdown=on_shutdown)
