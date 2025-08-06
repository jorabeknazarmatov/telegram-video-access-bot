from aiogram import Bot, Dispatcher, Router
from aiogram.enums.chat_member_status import ChatMemberStatus
from aiogram.types import Message 
import os, asyncio, logging, dotenv
from middleware import RoleCheckerMiddleware
from aiogram.filters import CommandStart
from keyboards import keyboard
from db import database
from handlers import admin_handler, user_handler

dotenv.load_dotenv()

logger = logging.getLogger()

CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()

async def main():
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started')
    dp = Dispatcher()
    
    
    # ✅ Kirishni tekshiruvchi middleware
    dp.message.middleware(RoleCheckerMiddleware())

    # ✅ Routerlar
    dp.include_routers(admin_handler.router, user_handler.router, router)
    
    await dp.start_polling(bot)

@router.message(CommandStart)
async def start_command(message: Message):
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=os.getenv('CHANNEL_ID'), user_id=user_id)

        if member.status in [ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            await message.answer(f'👤 Welcome Admin {message.from_user.full_name}!', reply_markup=keyboard.admin_control_en)
            return
        elif member.status == ChatMemberStatus.MEMBER:
            if not database.find_user(message.from_user.id):
                database.add_user(message.from_user.id, message.from_user.full_name)
            await message.answer(f'👤 Salom {message.from_user.full_name}!')
            await message.answer(f"🔐 Kino kalitini yubor:")
        else:
            await message.answer("❗ Siz kanalga a’zo emassiz. Iltimos, avval kanalga a’zo bo‘ling.", reply_markup=keyboard.join_channel)
            
    except Exception as e:
        await message.answer("⚠️ Kanal tekshiruvda xatolik: " + str(e))

if __name__ == '__main__':
    asyncio.run(main())
