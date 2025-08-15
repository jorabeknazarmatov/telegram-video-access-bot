import os
import dotenv
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from db import database
from handlers import add_movie_form, find_movie, get_posts
from main import logger

dotenv.load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()
router.include_routers(add_movie_form.router, find_movie.router, get_posts.router)


@router.callback_query(F.data == "users")
async def all_user(callback: CallbackQuery):
    try:
        users = database.get_all_user()
        logger.info("All users bosildi")
        await callback.answer(f"👥 All users: {len(users)}")
    except Exception as e:
        logger.exception("Xatolik all_user handlerida: %s", e)
        await callback.answer("⚠️ Xatolik yuz berdi.")


@router.callback_query(F.data == 'find_user')
async def find_user(callback: CallbackQuery):
    try:
        logger.info("Find user bosildi")
        await callback.answer("Xozirda ishlab chiqish jarayonida.")
    except Exception as e:
        logger.exception("Xatolik find_user handlerida: %s", e)
        await callback.answer("⚠️ Xatolik yuz berdi.")


@router.callback_query(F.data == 'all_movies')
async def get_all_movies(callback: CallbackQuery):
    try:
        logger.info("All movies bosildi")
        movies = database.get_all_movies()

        if not movies:
            logger.warning("Bazadan kino topilmadi.")
            await bot.send_message(callback.message.chat.id, "❌ Kino topilmadi.")
            return

        movie_list = "\n".join(f"• {k['name']} ⸺ {k['key']}" for k in movies)
        await bot.send_message(callback.message.chat.id, movie_list)
        logger.info("Jami %s ta kino yuborildi.", len(movies))

    except Exception as e:
        logger.exception("Xatolik get_all_movies handlerida: %s", e)
        await bot.send_message(callback.message.chat.id, "⚠️ Xatolik yuz berdi.")
