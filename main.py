from aiogram import Bot, Dispatcher, html, Router
from aiogram.types import Message, CallbackQuery 
import os, asyncio, logging, dotenv
from middleware import RoleCheckerMiddleware
from aiogram.filters import CommandStart
from keyboards import keyboard
from db import database
from handlers import admin_handler, user_handler

dotenv.load_dotenv()

# logger = logging.getLogger()

CHANNEL_ID = os.getenv('CHANNEL_ID')
CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()

async def main():
    # logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started')
    dp = Dispatcher()
    
    
    # ✅ Kirishni tekshiruvchi middleware
    dp.message.middleware(RoleCheckerMiddleware())

    # ✅ Routerlar
    dp.include_routers(admin_handler.router, user_handler.router, router)
    
    await dp.start_polling(bot)

@router.message(CommandStart)
async def start_command(message: Message, role: str):
    admins = await bot.get_chat_administrators(CHAT_ID)
    admin_ids = [admin.user.id for admin in admins]
    
    if message.from_user.id in admin_ids and  CHAT_ID == message.chat.id:
        await message.answer(f'👤 Welcome Admin {message.from_user.full_name}!', reply_markup=keyboard.admin_control_en)
        return
        
    if not database.find_user(message.from_user.id):
        database.add_user(message.from_user.id, message.from_user.full_name)

    await message.answer(f'👤 Welcome {message.from_user.full_name}!')
    await message.answer(f"🔐 Send key:")

if __name__ == '__main__':
    asyncio.run(main())
