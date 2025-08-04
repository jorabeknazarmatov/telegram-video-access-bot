import os, dotenv, json
from aiogram import Router, html, F, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
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
    all_info = State()
    name = State()
    desc = State()
    category = State()
    actors = State()


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    state_name = await state.get_state()
    
    if state_name is None:
        await message.answer("❗ Siz hozir hech qanday jarayonda emassiz.")
        return

    await state.clear()
    await message.answer("❌ Jarayon bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    await message.answer("Bosh menu", reply_markup=keyboard.admin_control_en)

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
    await bot.send_message(callback.message.chat.id, f'Submit the film. (The file must not exceed 2 GB)')
    await state.set_state(FormMovie.movie)

# Set movie and poster
@router.message(FormMovie.movie)
async def add_movie(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❗️ Please send video file.")
        return

    await state.update_data(movie = message.video.file_id)
    
    await state.set_state(FormMovie.poster)
    await message.answer("Send poster of the file.")


# Set poster
@router.message(FormMovie.poster)
async def set_poster(message: Message, state: FSMContext):
    if not message.video:
        await message.answer("❗️ Please send foto file for poster.")
        return
    await state.update_data(poster = message.photo[0].file_id)
    await bot.send_message(message.chat.id, "Is there a data JSON?", reply_markup=keyboard.select_btn)

@router.callback_query(F.data == 'dict_yes')
async def set_dict(callback: CallbackQuery):
    await bot.send_message(callback.message.chat.id, 'Send JSON file.')
    await bot.send_message(callback.message.chat.id, 
                           """
                            Template:
                            {
                                'key' : 'GC_T_',
                                'name' : 'Film name (year)',
                                'desc' : 'Description for film.',
                                'actors' : 'Tom Henks, Rowan Atkinson',
                                'category' : ['Drama', 'Jinoyat'],
                                'imdb' : 9.3,
                                'kinopoisk' : 9.1,
                                'duration' : 142,
                                'country' : 'USA, Canada'
                            }
                            """
                           )
    
    await FSMContext.set_data(FormMovie.all_info)

@router.callback_query(F.data == 'dict_no')
async def no_dict(callback: CallbackQuery):
    await bot.send_message(callback.message.chat.id, 'Send name file.')
    await FSMContext.set_data(FormMovie.name) 
    

@router.message(FormMovie.all_info)
async def set_movie_info(message: Message, state: FSMContext):
    if not F.document.mime_type == 'aplication/json':
        await message.answer("❗️ Please send JSON file.")
        return

    document = message.document
    
    file = await message.bot.get_file(document.file_id)
    file_path = file.file_path
    file_data = await message.bot.download_file(file_path)

    json_content = await file_data.read()

    try:
        movie = json.loads(json_content)
        stat_data = await state.get_data()

        database.add_movie({
            'key' : movie['key'],
            'name' : movie['name'],
            'movie_id' : stat_data.get('movie'),
            'poster' : stat_data.get('poster'),
            'desc' : movie['desc'],
            'actors' : movie['actors'],
            'category': movie['category']                
        })
        database.add_info({
            'key' : movie['key'],
            'imdb' : movie['imdb'],
            'kinopoisk':movie['kinopoisk'],
            'duration' : movie['duration'],
            'country' :movie['country']
        })
        await state.clear()
        await message.answer(f"✅ film muvaffaqiyatli yuklandi!", reply_markup=keyboard.admin_control_en)

    except Exception as e:
        await message.answer("❌ JSON formatda xatolik bor: " + str(e))

# Set name
@router.message(FormMovie.name)
async def set_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❗️ Please send video name.")
        return
    await state.update_data(name = message.text)
    await message.answer('Send description of the file.')
    await state.set_state(FormMovie.desc)

# Set description
@router.message(FormMovie.desc)
async def set_name(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("❗️ Please send desctiption name.")
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
        await message.answer("❗️ Please, enter the list of actors in text form. (with commas): Tom cruise, Tom Hanks")
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
