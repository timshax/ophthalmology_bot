import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_database
from handlers.inline_handlers import router as inline_router  # Новый импорт

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


async def set_bot_commands(bot: Bot):
    """Установка команд меню для бота"""
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/menu", description="Показать меню"),
        BotCommand(command="/debug", description="Отладочная информация"),
    ]
    await bot.set_my_commands(commands)
    print("✅ Команды меню установлены")


async def main():
    """Основная функция запуска бота"""

    # Инициализация базы данных
    await init_database()

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Установка команд меню
    await set_bot_commands(bot)

    # Регистрация роутеров - ТОЛЬКО inline handlers
    dp.include_router(inline_router)

    print("🚀 Офтальмологический бот запускается...")
    print("🤖 Бот готов к работе!")
    print("📱 Используются Inline-кнопки (гарантированно работают)")

    try:
        # Запускаем polling
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при работе бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())