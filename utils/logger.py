import sys
from loguru import logger

# Настройка логирования
logger.remove()  # Удаляем стандартный обработчик

# Добавляем обработчик для вывода в консоль
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# Добавляем обработчик для записи в файл
logger.add(
    "logs/casino.log",
    rotation="1 day",  # Ротация логов каждый день
    retention="7 days",  # Хранить логи 7 дней
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG"
) 