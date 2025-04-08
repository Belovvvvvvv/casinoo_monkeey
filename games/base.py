from abc import ABC, abstractmethod
from aiogram.types import Message
from database.db import Database
from payment.crypto import CryptoPayment
from utils.logger import logger

class BaseGame(ABC):
    def __init__(self, db: Database, crypto: CryptoPayment):
        self.db = db
        self.crypto = crypto
        self.game_name = self.__class__.__name__.lower().replace('game', '')

    @abstractmethod
    async def play(self, message: Message):
        pass

    async def check_balance(self, user_id: int, bet: float) -> bool:
        try:
            balance = await self.db.get_balance(user_id)
            if balance < bet:
                logger.warning(f"Недостаточно средств у пользователя {user_id}: баланс {balance}, ставка {bet}")
                return False
            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке баланса пользователя {user_id}: {str(e)}")
            raise

    async def process_win(self, user_id: int, bet: float, win_amount: float):
        try:
            await self.db.update_balance(user_id, win_amount)
            logger.success(f"Пользователь {user_id} выиграл {win_amount} монет (ставка: {bet})")
        except Exception as e:
            logger.error(f"Ошибка при обработке выигрыша пользователя {user_id}: {str(e)}")
            raise

    async def process_loss(self, user_id: int, bet: float):
        try:
            await self.db.update_balance(user_id, -bet)
        except Exception as e:
            logger.error(f"Ошибка при обработке проигрыша пользователя {user_id}: {str(e)}")
            raise

    async def get_bet(self, message, min_bet: float) -> float:
        try:
            bet = float(message.text.split()[1])
            if bet < min_bet:
                logger.warning(f"Пользователь {message.from_user.id} указал ставку меньше минимальной: {bet}")
                await message.answer(f"Минимальная ставка - {min_bet} монет")
                return None
            return bet
        except (IndexError, ValueError):
            await message.answer(f"Использование: {message.text.split()[0]} [ставка]\nПример: {message.text.split()[0]} {min_bet}")
            return None 