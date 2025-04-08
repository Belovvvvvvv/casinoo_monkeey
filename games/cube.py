import asyncio
from aiogram.types import Message
from games.base import BaseGame
from config import GAME_SETTINGS
from utils.logger import logger

class CubeGame(BaseGame):
    def __init__(self, db, crypto):
        super().__init__(db, crypto)
        self.min_bet = 1
        self.win_multiplier = 1.6

    async def play(self, message):
        try:
            user_id = message.from_user.id

            bet = await self.get_bet(message, self.min_bet)
            if bet is None:
                return

            if not await self.check_balance(user_id, bet):
                await message.answer("Недостаточно средств на балансе")
                return

            cube_msg = await message.answer_dice(emoji="🎲")
            await asyncio.sleep(4)

            score = cube_msg.dice.value

            if score == 6: 
                win_amount = bet * self.win_multiplier
                await self.process_win(user_id, bet, win_amount)
                await message.answer(f"🎲 Поздравляем! Вы выиграли {win_amount} монет!")
            else:
                await self.process_loss(user_id, bet)
                await message.answer(f"🎲 К сожалению, вы проиграли {bet} монет")

        except Exception as e:
            logger.error(f"Ошибка в игре кубик для пользователя {message.from_user.id}: {str(e)}")
            await message.answer("Произошла ошибка. Попробуйте позже.") 