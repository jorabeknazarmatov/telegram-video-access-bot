import os, dotenv
from aiogram import Router, html, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import keyboard
from db import database, key_generate
from main import CHAT_ID, CHANNEL_ID


dotenv.load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()

class FormMovie(StatesGroup):
    movie = State()
    poster = State()
    name = State()
    desc = State()
    category = State()
    actors = State()


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

@router.callback_query(F.data == 'find_movies')
async def find_muvie(callback: CallbackQuery):
    await callback.answer("Xozirda ishlab chiqish jarayonida.")

@router.callback_query(F.data == 'post_channel')
async def add_posts(callback: CallbackQuery):
    await callback.answer("Xozirda ishlab chiqish jarayonida.")

# Start FormMovie
@router.callback_query(F.data == "add_movie")
async def form_movie(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.message.chat.id, f'Submit the film. (The file must not exceed 2 GB)', reply_markup=keyboard.cancel_keyboard)
    await state.set_state(FormMovie.movie)

# Set movie and poster
@router.message(FormMovie.movie)
async def add_movie(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❗️ Please send video file.", reply_markup=keyboard.cancel_keyboard)
        return

    await state.update_data(movie = message.video.file_id)
    
    await state.set_state(FormMovie.poster)
    await message.answer("Send poster of the file.", reply_markup=keyboard.cancel_keyboard)


# Set poster
@router.message(FormMovie.poster)
async def set_poster(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❗️ Please send foto file for poster.", reply_markup=keyboard.cancel_keyboard)
        return
    await state.update_data(poster = message.photo[0].file_id)
    await bot.send_message("Send name of the file.", reply_markup=keyboard.cancel_keyboard)
    await state.set_data(FormMovie.name)

# Set name
@router.message(FormMovie.name)
async def set_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❗️ Please send video name.", reply_markup=keyboard.cancel_keyboard)
        return
    await state.update_data(name = message.text)
    await message.answer('Send description of the file.', reply_markup=keyboard.cancel_keyboard)
    await state.set_state(FormMovie.desc)

# Set description
@router.message(FormMovie.desc)
async def set_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❗️ Please send desctiption name.", reply_markup=keyboard.cancel_keyboard)
        return
    await state.update_data(desc = message.text)
    await message.answer('Send category of the file.', reply_markup=keyboard.build_category_keyboard())
    await state.set_state(FormMovie.category)

# Set category
@router.callback_query(FormMovie.category)
async def set_categories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("categories", [])

    if callback.data.startswith("cat:"):
        category = callback.data.split(":", 1)[1]

        # 🔄 Toggle qilish: qo‘shish/olib tashlash
        if category in selected:
            selected.remove(category)
        else:
            selected.append(category)

        # 🔄 State’ni yangilaymiz
        await state.update_data(categories=selected)

        # 🔄 Keyboardni qaytadan chizamiz
        await callback.message.edit_reply_markup(
            reply_markup=keyboard.build_category_keyboard(selected)
        )

        # ✅ Javob berish (shunchaki "popup" ga to‘sqinlik qilmaslik uchun)
        await callback.answer()

    elif callback.data == "submit":
        # 🔚 Tanlash yakunlandi
        await callback.answer("✅ Tanlov yakunlandi!")
        data = await state.get_data()
        selected_categories = data.get("categories", [])
        
        await callback.message.answer(
            f"Siz tanlagan kategoriyalar:\n" + "\n".join(f"• {k}" for k in selected_categories)
        )
        await callback.message.edit_reply_markup(reply_markup=None)
        await state.set_state(FormMovie.actors)
        await callback.message.answer("Enter a list of stars (with commas):")

# Set actors
@router.message(FormMovie.actors)
async def set_actors(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❗️ Please, enter the list of actors in text form. (with commas): Tom cruise, Tom Hanks", reply_markup=keyboard.cancel_keyboard)
        return
    await state.update_data(actors=message.text)
    
    data = await state.get_data() 
    key = key_generate()
    
    # Added movie to db
    database.add_movie(key, data.get('name'), data.get('movie'), data.get('poster'), data.get('desc'), data.get('actors', []), data.get('categories', []))


    await message.answer(f"✅ Success!", reply_markup=ReplyKeyboardRemove())
    await message.answer(
        f"Key: {html.bold(key)}\n"
        f"🎞 Name: {data.get('name')}\n"
        f"📝 Description: {data.get('desc')}\n"
        f"🎭 Actors: {data.get('actors')}\n"
        f"📁 Categories:\n" + ", ".join(k for k in data.get('categories', []))
    , reply_markup=keyboard.admin_control_en)
    
    await state.clear()


@router.message(F.text == '❌ Cancel')
async def click_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Jarayon bekor qilindi.", reply_markup=ReplyKeyboardRemove())
