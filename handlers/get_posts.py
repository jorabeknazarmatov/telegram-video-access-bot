import os, dotenv, json, random
from aiogram import Router, html, F, Bot
from aiogram.types import CallbackQuery
from db import database
from main import logger


dotenv.load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()

@router.callback_query(F.data == 'post_channel')
async def add_posts(callback: CallbackQuery):
    try:
        logger.info("Step 1: Fetching all movies from database.")
        all_movies = database.get_all_movies()

        if not all_movies:
            logger.warning("No movies found in database.")
            await callback.answer("Bazadan kino topilmadi.", show_alert=True)
            return

        logger.info("Step 2: Selecting 5 random movies for posting.")
        count = min(len(all_movies), 5)
        for movie in random.sample(all_movies, count):
            try:
                logger.info("Posting movie: %s", movie['name'])

                await bot.send_photo(
                    chat_id=os.getenv('CHANNEL_ID'),
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

            except Exception as e:
                logger.exception("Error while sending movie '%s': %s", movie.get('name', 'Unknown'), e)

        logger.info("Step 3: All posts sent successfully.")
        await callback.answer("Postlar kanalga yuborildi.", show_alert=True)

    except Exception as e:
        logger.exception("Unexpected error in add_posts: %s", e)
        await callback.answer("Xatolik yuz berdi. Qayta urinib ko‘ring.", show_alert=True)