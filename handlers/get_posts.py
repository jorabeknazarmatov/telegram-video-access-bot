import os, dotenv, json, random
from aiogram import Router, html, F, Bot
from aiogram.types import CallbackQuery
from db import database

dotenv.load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()

@router.callback_query(F.data == 'post_channel')
async def add_posts(callback: CallbackQuery):
    all_movies = database.get_all_movies()
    for movie in random.sample(all_movies, 1):
        await bot.send_photo(
            chat_id= os.getenv('CHANNEL_ID'),
            photo=movie['poster_id'],
            caption=(
                f"📽 {html.bold(movie['name'])}\n"
                f"⭐️ IMDb: {movie['imdb']}  KP:{movie['kinopoisk']}\n"
                f"🕒 Davomiyligi: {movie['duration'] // 60} soat {movie['duration'] % 60} daqiqa\n\n"
                f"{movie['desc']}\n\n"
                f"{' | '.join(f'#{cat}' for cat in json.loads(movie['category']))}\n\n"
                f"🎁 Tomosha qilish uchun quyidagi maxfiy kodni botga yuboring: <code>{movie['key']}</code>\n\n"
                f"➡️ 🎬 {html.link('Ko‘rish', 'https://t.me/vaultfilmbot')}\n"
                f"📌 Kanalga obuna bo‘ling: @Premium_Kino_Club"
            ),
            parse_mode="HTML"
        )