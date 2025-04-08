import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from database.db import Database
from payment.crypto import CryptoPayment
from handlers.commands import CommandHandlers
from utils.logger import logger

async def main():
    logger.info("Запуск бота...")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    db = Database()
    crypto = CryptoPayment()

    await db.init_db()

    command_handlers = CommandHandlers(bot, dp, db, crypto)

    logger.info("Бот запущен и готов к работе")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("Критическая ошибка при запуске бота")
