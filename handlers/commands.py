from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.db import Database
from payment.crypto import CryptoPayment
from games.bowling import BowlingGame
from games.darts import DartsGame
from games.cube import CubeGame
from utils.logger import logger
import asyncio

class CommandHandlers:
    def __init__(self, bot: Bot, dp: Dispatcher, db: Database, crypto: CryptoPayment):
        self.bot = bot
        self.dp = dp
        self.db = db
        self.crypto = crypto
        self.bowling_game = BowlingGame(db, crypto)
        self.darts_game = DartsGame(db, crypto)
        self.cube_game = CubeGame(db, crypto)
        
        # Регистрация обработчиков
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_balance, Command("balance"))
        self.dp.message.register(self.cmd_upbalance, Command("upbalance"))
        self.dp.message.register(self.cmd_bowling, Command("bowling"))
        self.dp.message.register(self.cmd_darts, Command("darts"))
        self.dp.message.register(self.cmd_cube, Command("cube"))

    async def cmd_start(self, message: Message):
        user_id = message.from_user.id
        await self.db.create_user(user_id)
        await message.answer(
            "Добро пожаловать в казино! 🎰\n\n"
            "Доступные игры:\n"
            "🎳 /bowling [ставка] - Игра в боулинг (мин. 10 монет, x3)\n"
            "🎯 /darts [ставка] - Игра в дартс (мин. 5 монет, выигрыш 5 монет)\n"
            "🎲 /cube [ставка] - Игра в кубик (мин. 1 монета, x1.6)\n\n"
            "💰 /balance - Проверить баланс\n"
            "💵 /upbalance [сумма] - Пополнить баланс"
        )

    async def cmd_balance(self, message: Message):
        user_id = message.from_user.id
        balance = await self.db.get_balance(user_id)
        await message.answer(f"Ваш баланс: {balance} монет")

    async def cmd_upbalance(self, message: Message):
        try:
            amount = float(message.text.split()[1])
            if amount < 1:
                await message.answer("Минимальная сумма пополнения - 1 USDT")
                return
            
            invoice = await self.crypto.create_invoice(message.from_user.id, amount)
            if invoice:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="💳 Оплатить",
                                url=invoice["bot_invoice_url"]
                            )
                        ]
                    ]
                )
                
                await message.answer(
                    f"Для пополнения баланса на {amount} USDT:\n\n"
                    f"Вам необходимо оплатить счет:\n"
                    f"`{invoice['bot_invoice_url']}`\n\n"
                    "После оплаты баланс будет автоматически пополнен.",
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )

                # Запускаем проверку статуса платежа
                asyncio.create_task(self.check_payment_status(invoice["invoice_id"], message.from_user.id, amount))
            else:
                logger.error(f"Ошибка при создании счета для пользователя {message.from_user.id}: {amount} USDT")
                await message.answer("Произошла ошибка при создании платежа. Попробуйте позже.")
        except (IndexError, ValueError):
            await message.answer("Использование: /upbalance [сумма]\nПример: /upbalance 10")

    async def check_payment_status(self, invoice_id: str, user_id: int, amount: float):
        """Проверяет статус платежа каждые 5 секунд"""
        while True:
            try:
                if await self.crypto.check_payment(invoice_id):
                    # Пополняем баланс
                    await self.db.update_balance(user_id, amount)
                    await self.bot.send_message(
                        user_id,
                        f"✅ Ваш баланс успешно пополнен на {amount} монет!"
                    )
                    break
            except Exception as e:
                logger.error(f"Ошибка при проверке платежа для пользователя {user_id}: {str(e)}")
            
            await asyncio.sleep(5)  # Проверяем каждые 5 секунд

    async def cmd_bowling(self, message: Message):
        await self.bowling_game.play(message)

    async def cmd_darts(self, message: Message):
        await self.darts_game.play(message)

    async def cmd_cube(self, message: Message):
        await self.cube_game.play(message) 