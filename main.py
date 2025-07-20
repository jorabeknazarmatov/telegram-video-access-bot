from aiogram import Bot, Dispatcher, html, Router
from aiogram.types import Message, CallbackQuery 
import os, asyncio, logging, dotenv
from middleware import RoleCheckerMiddleware
from aiogram.filters import CommandStart
from keyboards import keyboard
from db import database
from handlers import admin_handler, user_handler

dotenv.load_dotenv()

logger = logging.getLogger()

router = Router()

async def main():
    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started')
    bot = Bot(os.getenv('BOT_TOKEN'))
    dp = Dispatcher()
    
    # ✅ Kirishni tekshiruvchi middleware
    dp.message.middleware(RoleCheckerMiddleware())

    # ✅ Routerlar
    dp.include_routers(admin_handler.router, user_handler.router, router)
    
    await dp.start_polling(bot)

@router.message(CommandStart)
async def start_command(message: Message, role: str):
    if role != 'user':
        await message.answer('👤 Welcome Admin!', reply_markup=keyboard.admin_control_en)
        return
        
    if not database.find_user(message.from_user.id):
        database.add_user(message.from_user.id, message.from_user.full_name)

    await message.answer(f'👤 Welcome {message.from_user.full_name}!')
    await message.answer(f"Send me the video key:")

if __name__ == '__main__':
    asyncio.run(main())