import os, dotenv
from aiogram import Router, F, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db import database

dotenv.load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()

class FindMovie(StatesGroup):
    key = State()

@router.callback_query(F.data == 'find_movies')
async def find_muvie(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Kino kalitini yuboring.")
    await state.set_state(FindMovie.key)

@router.message(FindMovie.key)
async def find_key(message: Message, state: FSMContext):
    if not message.text.startswith(os.getenv('MOVIE_KEY')):
        await message.answer("Kalit xato yozilgan. Tekshirib qaytadan urinib ko'ring")
        return
    
    movie = database.get_movie(message.text.strip())
    if movie:
        text = (
            f"<b>{movie['name']}</b>\n\n"
            f"<b>⭐ IMDb:</b> {movie['imdb']}, <b>KP:</b> {movie['kinopoisk']}\n"
            f"{movie['desc']}\n\n"
            f"<b>🎭 Aktyorlar:</b> {movie['actors']}\n"
            f"<b>⏱ Davomiylik:</b> 0{int(movie['duration']) // 60}: {int(movie['duration']) % 60} daqiqa\n"
            f"<b>📁 Kategoriya:</b> {movie['category']}\n"
            f"<b>🌍 Davlat:</b> {movie['country']}\n"
        )
        await bot.send_photo(chat_id=message.chat.id, photo=movie['poster_id'], caption=text, parse_mode=ParseMode.HTML)
    else:
        await message.answer('❌ Bunday kalit mavjud emas.')
    
    await state.clear()