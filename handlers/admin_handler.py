import os, dotenv
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from db import database
from handlers import add_movie_form, find_movie, get_posts


dotenv.load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()
router.include_routers(add_movie_form.router, find_movie.router, get_posts.router)

@router.callback_query(F.data == "users")
async def all_user(callback: CallbackQuery):
    await callback.answer(f"👥 All users: {len(database.get_all_user())}")

@router.callback_query(F.data == 'find_user')
async def find_user(callback: CallbackQuery):
    await callback.answer("Xozirda ishlab chiqish jarayonida.")

@router.callback_query(F.data == 'all_movies')
async def get_all_movies(callback: CallbackQuery):
    movies = database.get_all_movies()
    await bot.send_message(callback.message.chat.id, "\n".join(f"• {k[1]} ⸺ {k[0]}" for k in movies))

