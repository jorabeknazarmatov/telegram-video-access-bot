from aiogram import Router, html, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from db import database
import os, dotenv, json

dotenv.load_dotenv()

router = Router()

@router.message(F.text.startswith("GC_T_"))
async def movie_code(message: Message):
    movie = database.get_movie(message.text.strip())
    if not movie:
        await message.answer("❌ Not correct key.")
        return
    else:
        await message.answer_video(
        video=movie['movie_id'],
        caption=(
            f"📽 {html.bold(movie['name'])}\n"
            f"⭐️ IMDb: {movie['imdb']}\n"
            f"🕒 Davomiyligi: {movie['duration'] // 60} soat {movie['duration'] % 60} daqiqa\n\n"
            f"{movie['desc']}\n\n"
            f"{' | '.join(f'#{cat}' for cat in json.loads(movie['category']))}\n\n"
            f"🎁 Tomosha qilish uchun quyidagi maxfiy kodni botga yuboring: <code>{movie['key']}</code>\n\n"
            f"➡️ 🎬 {html.link('Ko‘rish', 'https://t.me/vaultfilmbot')}\n"
            f"📌 Kanalga obuna bo‘ling: @Premium_Kino_Club"
        ),
        parse_mode="HTML"
    )
