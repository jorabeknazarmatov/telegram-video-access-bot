import os, dotenv, json
from aiogram import Router, html, F, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards import keyboard
from db import database, key_generate
from main import logger

dotenv.load_dotenv()
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()


class FormMovie(StatesGroup):
    key = State()
    movie = State()
    poster_id = State()
    all_info = State()
    name = State()
    desc = State()
    category = State()
    actors = State()


@router.message(Command("cancel"))
async def cancel_command(message: Message, state: FSMContext):
    try:
        logger.info("Cancel buyrug‘i ishga tushdi.")
        state_name = await state.get_state()

        if state_name is None:
            logger.warning("Cancel bosildi, ammo foydalanuvchi hech qanday jarayonda emas.")
            await message.answer("❗ Siz hozir hech qanday jarayonda emassiz.")
            return

        await state.clear()
        logger.info("❌ Jarayon foydalanuvchi tomonidan bekor qilindi.")
        await message.answer("❌ Jarayon bekor qilindi.", reply_markup=ReplyKeyboardRemove())
        await message.answer("Bosh menu", reply_markup=keyboard.admin_control_en)

    except Exception as e:
        logger.exception("Cancel command bajarishda xatolik: %s", e)
        await message.answer("⚠️ Xatolik yuz berdi. Keyinroq qayta urinib ko‘ring.")


# Start FormMovie
@router.callback_query(F.data == "add_movie")
async def form_movie(callback: CallbackQuery, state: FSMContext):
    try:
        logger.info("Admin kino qo‘shish jarayonini boshladi. UserID: %s", callback.from_user.id)
        
        await bot.send_message(
            callback.message.chat.id,
            "Submit the film. (The file must not exceed 2 GB)"
        )
        await state.set_state(FormMovie.movie)
        
        logger.info("Holat FormMovie.movie ga o‘tkazildi.")

    except Exception as e:
        logger.exception("Kino qo‘shish jarayonini boshlashda xatolik: %s", e)
        await callback.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.", show_alert=True)


# Set movie and poster
@router.message(FormMovie.movie)
async def add_movie(message: Message, state: FSMContext):
    try:
        logger.info("Video qabul qilish bosqichi boshlandi. UserID: %s", message.from_user.id)

        if not message.video:
            logger.warning("Video fayl yuborilmagan. UserID: %s", message.from_user.id)
            await message.answer("❗️ Please send video file.")
            return

        movie_key = key_generate()
        await state.update_data(key=movie_key, movie=message.video.file_id)
        
        logger.info("✅ Video yuklandi. Key: %s | FileID: %s", movie_key, message.video.file_id)

        await state.set_state(FormMovie.poster_id)
        await message.answer("Send poster of the file.")

    except Exception as e:
        logger.exception("Video qabul qilishda xatolik: %s", e)
        await message.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.")



# Set poster
@router.message(FormMovie.poster_id)
@router.message(FormMovie.poster_id)
async def set_poster(message: Message, state: FSMContext):
    try:
        logger.info("Poster qabul qilish bosqichi boshlandi. UserID: %s", message.from_user.id)

        if not message.photo:
            logger.warning("Poster yuborilmagan. UserID: %s", message.from_user.id)
            await message.answer("❗️ Please send foto file for poster.")
            return

        poster_id = message.photo[0].file_id
        await state.update_data(poster_id=poster_id)
        
        logger.info("✅ Poster yuklandi. PosterID: %s", poster_id)

        await bot.send_message(
            message.chat.id,
            "Is there a data JSON?",
            reply_markup=keyboard.select_btn
        )

    except Exception as e:
        logger.exception("Poster qabul qilishda xatolik: %s", e)
        await message.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.")


@router.callback_query(F.data == 'dict_yes')
async def set_dict(callback: CallbackQuery, state: FSMContext):
    try:
        logger.info(
            "JSON ma'lumot yuklash jarayoni boshlandi. UserID: %s",
            callback.from_user.id
        )

        await bot.send_message(callback.message.chat.id, 'Send JSON file.')
        
        template = """
<pre>
{
    "name": "Film name (year)",
    "desc": "Description for film.",
    "actors": "Tom Henks, Rowan Atkinson",
    "category": ["Drama", "Jinoyat"],
    "imdb": 9.3,
    "kinopoisk": 9.1,
    "duration": 142,
    "country": "USA, Canada"
}
</pre>
"""
        await bot.send_message(
            callback.message.chat.id,
            template,
            parse_mode=ParseMode.HTML
        )

        await state.set_state(FormMovie.all_info)
        logger.info("Holat FormMovie.all_info ga o‘tkazildi. UserID: %s", callback.from_user.id)

    except Exception as e:
        logger.exception("JSON yuklash jarayonini boshlashda xatolik: %s", e)
        await callback.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.", show_alert=True)


@router.message(FormMovie.all_info)
async def set_movie_info(message: Message, state: FSMContext):
    try:
        logger.info(
            "JSON fayl qabul qilish bosqichi boshlandi. UserID: %s",
            message.from_user.id
        )

        # 1. Fayl formati tekshiriladi
        if message.document.mime_type != 'application/json':
            logger.warning("JSON emas bo'lgan fayl yuborildi. UserID: %s", message.from_user.id)
            await message.answer("❗️ Please send JSON file.")
            return

        # 2. Faylni yuklab olish
        document = message.document
        file = await message.bot.get_file(document.file_id)
        file_data = await message.bot.download_file(file.file_path)

        # 3. Faylni dekodlash
        content = file_data.read().decode('utf-8')
        movie = json.loads(content)
        logger.info("✅ JSON fayl muvaffaqiyatli o‘qildi. UserID: %s", message.from_user.id)

        # 4. Kerakli maydonlarni tekshirish
        required_fields = ['name', 'desc', 'actors', 'category', 'imdb', 'kinopoisk', 'duration', 'country']
        for field in required_fields:
            if field not in movie:
                logger.warning("JSON faylda '%s' maydon yetishmayapti. UserID: %s", field, message.from_user.id)
                await message.answer(f"❌ Required field missing: '{field}'")
                return

        # 5. State'dagi ma'lumotlarni olish
        stat_data = await state.get_data()

        # 6. Bazaga yozish
        database.add_movie({
            'key': stat_data.get('key'),
            'name': movie['name'],
            'movie_id': stat_data.get('movie'),
            'poster_id': stat_data.get('poster_id'),
            'desc': movie['desc'],
            'actors': movie['actors'],
            'category': movie['category']
        })

        database.add_info({
            'key': stat_data.get('key'),
            'imdb': movie['imdb'],
            'kinopoisk': movie['kinopoisk'],
            'duration': movie['duration'],
            'country': movie['country']
        })

        # 7. Jarayon yakuni
        await state.clear()
        logger.info("✅ Film ma'lumotlari muvaffaqiyatli bazaga qo‘shildi. UserID: %s", message.from_user.id)
        await message.answer("✅ Film muvaffaqiyatli yuklandi!", reply_markup=keyboard.admin_control_en)

    except Exception as e:
        logger.exception("JSON faylni qayta ishlashda xatolik: %s", e)
        await message.answer(f"❌ JSON formatda xatolik bor:\n<code>{e}</code>", parse_mode=ParseMode.HTML)


@router.callback_query(F.data == 'dict_no')
async def no_dict(callback: CallbackQuery, state: FSMContext):
    try:
        logger.info(
            "Admin JSONsiz kino ma'lumotlarini kiritishni tanladi. UserID: %s",
            callback.from_user.id
        )

        await bot.send_message(callback.message.chat.id, 'Send name file.')
        await state.set_state(FormMovie.name)

        logger.info("Holat FormMovie.name ga o‘tkazildi. UserID: %s", callback.from_user.id)

    except Exception as e:
        logger.exception("dict_no jarayonini boshlashda xatolik: %s", e)
        await callback.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.", show_alert=True)


# Set name
@router.message(FormMovie.name)
async def set_name(message: Message, state: FSMContext):
    try:
        logger.info(
            "Film nomini qabul qilish bosqichi boshlandi. UserID: %s",
            message.from_user.id
        )

        if not message.text:
            logger.warning("Film nomi matn sifatida yuborilmadi. UserID: %s", message.from_user.id)
            await message.answer("❗️ Please send video name.")
            return

        await state.update_data(name=message.text)
        logger.info("✅ Film nomi qabul qilindi: %s", message.text)

        await message.answer('Send description of the file.')
        await state.set_state(FormMovie.desc)
        logger.info("Holat FormMovie.desc ga o‘tkazildi. UserID: %s", message.from_user.id)

    except Exception as e:
        logger.exception("Film nomini qabul qilishda xatolik: %s", e)
        await message.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.")


# Set description
@router.message(FormMovie.desc)
async def set_desc(message: Message, state: FSMContext):
    try:
        logger.info(
            "Film tavsifini qabul qilish bosqichi boshlandi. UserID: %s",
            message.from_user.id
        )

        if not message.text:
            logger.warning("Film tavsifi matn sifatida yuborilmadi. UserID: %s", message.from_user.id)
            await message.answer("❗️ Please send description name.")
            return

        await state.update_data(desc=message.text)
        logger.info("✅ Film tavsifi qabul qilindi. Uzunligi: %d belgilar", len(message.text))

        await message.answer('Send category of the file.', reply_markup=keyboard.build_category_keyboard())
        await state.set_state(FormMovie.category)
        logger.info("Holat FormMovie.category ga o‘tkazildi. UserID: %s", message.from_user.id)

    except Exception as e:
        logger.exception("Film tavsifini qabul qilishda xatolik: %s", e)
        await message.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.")


# Set category
@router.callback_query(FormMovie.category)
async def set_categories(callback: CallbackQuery, state: FSMContext):
    try:
        logger.info(
            "Kategoriya tanlash bosqichi boshlandi. UserID: %s",
            callback.from_user.id
        )

        data = await state.get_data()
        selected = data.get("categories", [])

        if callback.data.startswith("cat:"):
            category = callback.data.split(":", 1)[1]

            # Toggle qilish: qo‘shish yoki olib tashlash
            if category in selected:
                selected.remove(category)
                logger.info("Kategoriya o‘chirildi: %s", category)
            else:
                selected.append(category)
                logger.info("Kategoriya qo‘shildi: %s", category)

            # State yangilash
            await state.update_data(categories=selected)

            # Keyboard qayta chizish
            await callback.message.edit_reply_markup(
                reply_markup=keyboard.build_category_keyboard(selected)
            )

            # Popup javobi
            await callback.answer()

        elif callback.data == "submit":
            # Yakunlash
            await callback.answer("✅ Tanlov yakunlandi!")
            selected_categories = data.get("categories", [])

            logger.info(
                "Kategoriya tanlash yakunlandi. Tanlanganlar: %s",
                ", ".join(selected_categories)
            )

            await callback.message.answer(
                "Siz tanlagan kategoriyalar:\n" + "\n".join(f"• {k}" for k in selected_categories)
            )
            await callback.message.edit_reply_markup(reply_markup=None)

            await state.set_state(FormMovie.actors)
            logger.info("Holat FormMovie.actors ga o‘tkazildi. UserID: %s", callback.from_user.id)
            await callback.message.answer("Enter a list of stars (with commas):")

    except Exception as e:
        logger.exception("Kategoriya tanlash jarayonida xatolik: %s", e)
        await callback.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.", show_alert=True)


# Set actors
@router.message(FormMovie.actors)
async def set_actors(message: Message, state: FSMContext):
    try:
        logger.info(
            "Aktyorlar ro‘yxatini qabul qilish bosqichi boshlandi. UserID: %s",
            message.from_user.id
        )

        if not message.text:
            logger.warning("Aktyorlar matn ko‘rinishida yuborilmadi. UserID: %s", message.from_user.id)
            await message.answer(
                "❗️ Please, enter the list of actors in text form. (with commas): Tom Cruise, Tom Hanks"
            )
            return

        await state.update_data(actors=message.text)
        logger.info("✅ Aktyorlar qabul qilindi: %s", message.text)

        data = await state.get_data()

        # Ma'lumotlarni bazaga yozish
        database.add_movie({
            'key': data.get('key'),
            'name': data.get('name'),
            'movie_id': data.get('movie'),
            'poster_id': data.get('poster_id'),
            'desc': data.get('desc'),
            'actors': data.get('actors', []),
            'category': data.get('categories', [])
        })

        logger.info("Film ma'lumotlari bazaga qo‘shildi. Key: %s", data.get('key'))

        await message.answer("✅ Success!", reply_markup=ReplyKeyboardRemove())
        await message.answer(
            f"Key: {html.bold(data.get('key'))}\n"
            f"🎞 Name: {data.get('name')}\n"
            f"📝 Description: {data.get('desc')}\n"
            f"🎭 Actors: {data.get('actors')}\n"
            f"📁 Categories:\n" + ", ".join(k for k in data.get('categories', [])),
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard.admin_control_en
        )

        await state.clear()
        logger.info("✅ Film yuklash jarayoni yakunlandi. UserID: %s", message.from_user.id)

    except Exception as e:
        logger.exception("Aktyorlar bosqichida xatolik: %s", e)
        await message.answer("⚠️ Xatolik yuz berdi. Qayta urinib ko‘ring.")   