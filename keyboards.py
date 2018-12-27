from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Adult content keyboard
_inline_btn_adult_yes = InlineKeyboardButton('Yes', callback_data='adult_true')
_inline_btn_adult_no = InlineKeyboardButton('No', callback_data='adult_false')
inline_adult_kb = InlineKeyboardMarkup().row(_inline_btn_adult_yes, _inline_btn_adult_no)

# Languages keyboard
_inline_btn_lang_en = InlineKeyboardButton('English', callback_data='lang_en')
_inline_btn_lang_ru = InlineKeyboardButton('Русский', callback_data='lang_ru')
_inline_btn_lang_de = InlineKeyboardButton('Deutsch', callback_data='lang_de')
_inline_btn_lang_fr = InlineKeyboardButton('Français', callback_data='lang_fr')
_inline_btn_lang_es = InlineKeyboardButton('Español', callback_data='lang_es')
_inline_btn_lang_zh = InlineKeyboardButton('漢語', callback_data='lang_zh')
inline_lang_kb = InlineKeyboardMarkup()
inline_lang_kb.row(_inline_btn_lang_en, _inline_btn_lang_ru)
inline_lang_kb.row(_inline_btn_lang_de, _inline_btn_lang_fr)
inline_lang_kb.row(_inline_btn_lang_es, _inline_btn_lang_zh)

# Settings keyboard
_inline_btn_settings_langs = InlineKeyboardButton('Language', callback_data='settings_lang')
_inline_btn_settings_adult = InlineKeyboardButton('Adult content', callback_data='settings_adult')
inline_settings_kb = InlineKeyboardMarkup()
inline_settings_kb.add(_inline_btn_settings_langs)
inline_settings_kb.add(_inline_btn_settings_adult)

# Keyboard for showing more movies
_inline_btn_movies = InlineKeyboardButton('Show more', callback_data='show_more')
inline_more_movies_kb = InlineKeyboardMarkup().add(_inline_btn_movies)
