from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


admin_control_en = InlineKeyboardMarkup(
    inline_keyboard = [
        [InlineKeyboardButton(text='👥 All users', callback_data='users')],
        [InlineKeyboardButton(text='🎞 All movies', callback_data='all_movies')],
        [InlineKeyboardButton(text='🎥 Add movie', callback_data='add_movie')]
    ], 
)

categories = [
    ("Action", "action"),
    ("Anime", "anime"),
    ("Comedy", "comedy"),
    ("Cartoon", "cartoon"),
    ("Documentary", "documentary"),
    ("Drama", "drama"),
    ("Fantasy", "fantasy"),
    ("Horror", "horror"),
    ("Musical", "musical"),
    ("Mystery", "mystery"),
    ("Romance", "romance"),
    ("Science Fiction", "science_fiction"),
    ("Thriller", "thriller"),
    ("Western", "western"),
    ("+18", "+18")
]


def build_category_keyboard(selected: list = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    selected = selected or []

    for text, callback in categories:
        is_selected = "✅ " if callback in selected else ""
        builder.button(
            text=is_selected + text,
            callback_data=f"cat:{callback}"
        )

    builder.button(text="📤 Submit", callback_data="submit")
    builder.adjust(2, repeat=True)  

    return builder.as_markup()
