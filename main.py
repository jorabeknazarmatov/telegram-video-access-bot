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

# Logger sozlash
logging.basicConfig(
    filename='myapp.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

CHAT_ID = os.getenv('CHAT_ID')
bot = Bot(os.getenv('BOT_TOKEN'))
router = Router()

async def main():
    try:
        logger.info('🚀 Bot ishga tushirilmoqda...')
        dp = Dispatcher()
        
        # ✅ Kirishni tekshiruvchi middleware
        dp.message.middleware(RoleCheckerMiddleware())

        # ✅ Routerlar
        dp.include_routers(admin_handler.router, user_handler.router, router)
        
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("❌ Bot ishga tushirishda xatolik: %s", e)

@router.message(CommandStart())
async def start_command(message: Message):
    logger.info("Start buyrug‘i kelib tushdi. UserID: %s", message.from_user.id)
    user_id = message.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=os.getenv('CHANNEL_ID'), user_id=user_id)
        logger.info("Kanal a'zolik statusi: %s", member.status)

        if member.status in [ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]:
            logger.info("Admin foydalanuvchi kirdi: %s", message.from_user.full_name)
            await message.answer(
                f'👤 Welcome Admin {message.from_user.full_name}!',
                reply_markup=keyboard.admin_control_en
            )

        elif member.status == ChatMemberStatus.MEMBER:
            if not database.find_user(user_id):
                database.add_user(user_id, message.from_user.full_name)
                logger.info("Foydalanuvchi bazaga qo‘shildi: %s", message.from_user.full_name)
            await message.answer(f'👤 Salom {message.from_user.full_name}!')
            await message.answer("🔐 Kino kalitini yubor:")

        else:
            logger.warning("Kanalga a'zo bo‘lmagan foydalanuvchi: %s", message.from_user.full_name)
            await message.answer(
                "❗ Siz kanalga a’zo emassiz. Iltimos, avval kanalga a’zo bo‘ling.",
                reply_markup=keyboard.join_channel
            )

    except Exception as e:
        logger.exception("⚠️ Kanal a'zolikni tekshirishda xatolik: %s", e)
        await message.answer("⚠️ Kanal tekshiruvda xatolik: " + str(e))

if __name__ == '__main__':
    asyncio.run(main())
