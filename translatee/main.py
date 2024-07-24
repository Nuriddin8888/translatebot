import logging
import aiohttp
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from database import * 
from buttons.inline import *

API_TOKEN = '7231442870:AAGfupxHgK6-_YnhklkZh_lMIAgLi5ixCn0'
API_URL = 'https://cvt.su/x/translator/?from=auto&to={}&text={}'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot)
dp.middleware.setup(LoggingMiddleware())

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

@dp.message_handler()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    lang_code = 'uz'

    translated_text = await translate_text(text, lang_code)

    add_translation(user_id, text, translated_text, lang_code)
    
    await message.answer(f"<code>{translated_text}</code>", parse_mode='HTML', reply_markup=get_language_keyboard(1))

@dp.callback_query_handler(lambda c: c.data.startswith('page_'))
async def handle_pagination(callback_query: types.CallbackQuery):
    page = int(callback_query.data.split('_')[1])
    await bot.answer_callback_query(callback_query.id)
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=get_language_keyboard(page))

@dp.callback_query_handler(lambda c: c.data in languages_dict.keys())
async def translate_text_handler(call: types.CallbackQuery):
    lang_code = call.data
    user_id = call.from_user.id

    text = call.message.text
    translated_text = await translate_text(text, lang_code)
    
    add_translation(user_id, text, translated_text, lang_code)
    
    await call.message.edit_text(f"<code>{translated_text}</code>", parse_mode='HTML', reply_markup=get_language_keyboard(1))
    await bot.answer_callback_query(call.id)

async def on_start_up(dp):
    await bot.send_message(chat_id=1921911753, text='Bot ishga tushdi!')

async def on_shutdown(dp):
    await bot.send_message(chat_id=1921911753, text='Bot o\'chdi!')

if __name__ == "__main__":
    init_db()
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up, on_shutdown=on_shutdown)