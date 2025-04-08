import sqlite3
from utils.logger import logger

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None

    async def init_db(self):
        try:
            self.conn = sqlite3.connect('casino.db')
            self.cursor = self.conn.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL DEFAULT 0
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {str(e)}")
            raise

    async def create_user(self, user_id: int):
        try:
            self.cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя {user_id}: {str(e)}")
            raise

    async def get_balance(self, user_id: int) -> float:
        try:
            self.cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0.0
        except Exception as e:
            logger.error(f"Ошибка при получении баланса пользователя {user_id}: {str(e)}")
            raise

    async def update_balance(self, user_id: int, amount: float):
        try:
            self.cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при обновлении баланса пользователя {user_id}: {str(e)}")
            raise

    def __del__(self):
        if self.conn:
            self.conn.close() 