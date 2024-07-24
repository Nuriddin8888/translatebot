from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

languages_dict = {
    'uz': "UZB 🇺🇿", 'en': "ENG 🇺🇸", 'ru': "RUS 🇷🇺", 'ko': "KOR 🇰🇷", 'zh-CN': "CN 🇨🇳",
    'de': "GER 🇩🇪", 'es': "ISP 🇪🇸", 'ar': "BAA 🇦🇪", 'tg': "TOJ 🇭🇺", 'ja': "JP 🇯🇵", 
    'kn': "CA 🇨🇦", 'tr': "TR 🇹🇷", 'fr': "FR 🇫🇷", 'it': "IT 🇮🇹", 'kk': "KZ 🇰🇿",
    'ky': "KG 🇰🇬", 'mn': "MN 🇲🇳", 'ne': "NP 🇳🇵", 'fa': "FA 🇮🇷", 'el': "GR 🇬🇷",
    'hi': "IN 🇮🇳", 'is': "IS 🇮🇸", 'id': "ID 🇮🇩", 'lv': "LV 🇱🇻", 'mk': "MK 🇲🇰"
}


def get_language_keyboard(page: int = 1):
    languages_per_page = 6
    language_keys = list(languages_dict.keys())
    start = (page - 1) * languages_per_page
    end = start + languages_per_page
    buttons = [InlineKeyboardButton(f"{languages_dict[code]}", callback_data=code) for code in language_keys[start:end]]
    
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(*buttons)
    

    if page > 1:
        keyboard.insert(InlineKeyboardButton("◀️ Prev", callback_data=f"page_{page-1}"))
    if end < len(language_keys):
        keyboard.insert(InlineKeyboardButton("Next ▶️", callback_data=f"page_{page+1}"))
    
    return keyboard



def admin_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Users", callback_data='users'))
    keyboard.add(InlineKeyboardButton("Bot Statistics", callback_data='statistics'))
    return keyboard