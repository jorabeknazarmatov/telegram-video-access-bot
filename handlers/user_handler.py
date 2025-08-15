from aiogram import Router, html, F
from aiogram.types import Message
from db import database
import os, dotenv, json
from logger import logger


dotenv.load_dotenv()

router = Router()

@router.message(F.text.startswith("GC_T_"))
async def movie_code(message: Message):
    try:
        key = message.text.strip()
        logger.info("Movie key received: %s", key)

        movie = database.get_movie(key)
        if not movie:
            logger.warning("Key not found in database: %s", key)
            await message.answer("❌ Bunday kalit mavjud emas.")
            return

        logger.info("Movie found: %s", movie['name'])

        await message.answer_video(
            video=movie['movie_id'],
            caption=(
                f"📽 {html.bold(movie['name'])}\n"
                f"⭐️ IMDb: {movie['imdb']}  KP: {movie['kinopoisk']}\n"
                f"🕒 Davomiyligi: {movie['duration'] // 60} soat {movie['duration'] % 60} daqiqa\n\n"
                f"{' | '.join(f'#{cat}' for cat in json.loads(movie['category']))}\n\n"
                f"📌 Kanalga obuna bo‘ling: @Premium_Kino_Club"
            ),
            parse_mode="HTML"
        )

        logger.info("Movie sent successfully: %s", movie['name'])

    except Exception as e:
        logger.exception("Unexpected error while sending movie for key: %s", message.text)
        await message.answer("⚠️ Xatolik yuz berdi. Keyinroq qayta urinib ko‘ring.")
