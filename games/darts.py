import asyncio
from aiogram.types import Message
from games.base import BaseGame
from config import GAME_SETTINGS
from utils.logger import logger

class DartsGame(BaseGame):
    def __init__(self, db, crypto):
        super().__init__(db, crypto)
        self.settings = GAME_SETTINGS['darts']
        self.min_bet = 5
        self.win_amount = 5
        logger.info("Инициализация игры в дартс")

    async def play(self, message):
        try:
            user_id = message.from_user.id

            bet = await self.get_bet(message, self.min_bet)
            if bet is None:
                return

            if not await self.check_balance(user_id, bet):
                await message.answer("Недостаточно средств на балансе")
                return

            darts_msg = await message.answer_dice(emoji="🎯")
            await asyncio.sleep(4)

            score = darts_msg.dice.value

            if score == 6: 
                await self.process_win(user_id, bet, self.win_amount)
                await message.answer(f"🎯 Поздравляем! Вы выиграли {self.win_amount} монет!")
            else:
                await self.process_loss(user_id, bet)
                await message.answer(f"🎯 К сожалению, вы проиграли {bet} монет")

        except Exception as e:
            logger.error(f"Ошибка в игре дартс для пользователя {message.from_user.id}: {str(e)}")
            await message.answer("Произошла ошибка. Попробуйте позже.")

    async def play_again(self, message):
        try:
            user_id = message.from_user.id
            logger.info(f"Пользователь {user_id} начал игру в дартс")
            
            bet = await self.get_bet(message, self.settings['min_bet'])
            if bet is None:
                return
            
            if not await self.check_balance(user_id, bet):
                logger.warning(f"У пользователя {user_id} недостаточно средств для ставки {bet}")
                await message.answer("Недостаточно средств на балансе")
                return
            
            await self.db.update_balance(user_id, -bet)
            
            darts_msg = await message.answer_dice(emoji="🎯")
            logger.info(f"Отправлена анимация дартса для пользователя {user_id}")
            
            await asyncio.sleep(4)
            
            score = darts_msg.dice.value
            logger.info(f"Результат броска дартса для пользователя {user_id}: {score}")
            
            if self.settings['win_condition'](score):
                win_amount = self.settings['win_amount']
                await self.process_win(
                    message, user_id, bet, win_amount,
                    "🎯", "Вы попали в центр!"
                )
                logger.success(f"Пользователь {user_id} выиграл в дартс: {win_amount} монет")
                await message.answer(f"🎯 Поздравляем! Вы попали в центр и выиграли {win_amount} монет!")
            else:
                await self.process_loss(
                    message, "🎯", f"Вы попали в {score}!", bet
                )
                logger.info(f"Пользователь {user_id} проиграл в дартс: {bet} монет")
        except Exception as e:
            logger.error(f"Ошибка в игре дартс для пользователя {message.from_user.id}: {str(e)}")
            await message.answer("Произошла ошибка. Попробуйте позже.") 