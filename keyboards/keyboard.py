from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


admin_control_en = InlineKeyboardMarkup(
    inline_keyboard=[
        # 👥 User Boshqaruv
        [
            InlineKeyboardButton(text='👥 All Users', callback_data='users'),
            InlineKeyboardButton(text='🔍 Find User', callback_data='find_user'),
        ],
        # 🎞 Film Boshqaruv
        [
            InlineKeyboardButton(text='🎞 All Movies', callback_data='all_movies'),
            InlineKeyboardButton(text='🔎 Find Movie', callback_data='find_movies'),
        ],
        [
            InlineKeyboardButton(text='➕ Add Movie', callback_data='add_movie'),
            InlineKeyboardButton(text='➕ Add Movies with JSON', callback_data='add_movies')
        ],
        # 📣 Chiqish (optional)
        [
            InlineKeyboardButton(text='📣 Post in the channel', callback_data='post_channel')
        ]
    ]
)

select_btn = InlineKeyboardMarkup(
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Yes', callback_data='dict_yes'),
            InlineKeyboardButton(text='No', callback_data='dict_no')
        ]
    ]
)

join_channel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='📢 Kanalga a’zo bo‘lish', url='https://t.me/Premium_Kino_Club')
        ]
    ]
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Cancel")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,  # bosilgach, avtomatik yo‘qoladi
    input_field_placeholder="Istalgan vaqtda bekor qilish mumkin"
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
