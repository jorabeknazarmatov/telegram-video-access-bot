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
            video=movie[2],
            caption=(
                f"🎬 {html.bold(movie[1])}\n"
                f"📝 {movie[4]}\n\n"
                f"{" | ".join(f'#{cat}' for cat in json.loads(movie[6]))}"
            ),
            parse_mode="HTML"
        )
