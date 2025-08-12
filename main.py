#!/usr/bin/env python3
"""
Главный файл для запуска Interview Helper Bot
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем src в путь для импортов
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import settings
from src.api import app
from src.telegram_bot import bot
from src.database import database

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_bot_sync():
    """Синхронный запуск бота: PTB сам управляет loop, БД управляется через post_init/post_shutdown."""
    try:
        logger.info("Запуск Telegram бота (polling)...")
        bot.run()  # блокирующий вызов PTB v20
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise


async def run_api():
    """Запуск только FastAPI сервера"""
    import uvicorn
    
    try:
        logger.info(f"Запуск FastAPI сервера на {settings.host}:{settings.port}")
        config = uvicorn.Config(
            app=app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower()
        )
        server = uvicorn.Server(config)
        await server.serve()
    except KeyboardInterrupt:
        logger.info("API сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске API сервера: {e}")
        raise


async def run_both():
    """Запуск и бота, и API сервера одновременно"""
    try:
        logger.info("Запуск бота и API сервера...")
        
        # Запускаем оба сервиса одновременно
        await asyncio.gather(
            run_bot(),
            run_api()
        )
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        raise


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Interview Helper Bot")
    parser.add_argument(
        "--mode",
        choices=["bot", "api", "both"],
        default="both",
        help="Режим запуска: bot (только бот), api (только API), both (оба)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == "bot":
            run_bot_sync()
        elif args.mode == "api":
            asyncio.run(run_api())
        else:  # both
            asyncio.run(run_both())
            
    except KeyboardInterrupt:
        logger.info("Приложение остановлено")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 