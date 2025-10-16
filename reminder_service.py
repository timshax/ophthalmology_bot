import asyncio
import aioschedule
from aiogram import Bot
from config import BOT_TOKEN
from database import send_reminders


async def send_daily_reminders():
    """Ежедневная отправка напоминаний"""
    bot = Bot(token=BOT_TOKEN)
    try:
        print("🔔 Запуск ежедневной отправки напоминаний...")
        sent_count = await send_reminders(bot)
        print(f"✅ Ежедневные напоминания отправлены: {sent_count} сообщений")
        return sent_count
    except Exception as e:
        print(f"❌ Ошибка при отправке напоминаний: {e}")
        return 0
    finally:
        await bot.session.close()


async def start_reminder_service():
    """Запуск сервиса напоминаний"""
    print("⏰ Сервис напоминаний запускается...")

    # Настройка расписания
    aioschedule.every().day.at("09:00").do(lambda: asyncio.create_task(send_daily_reminders()))
    aioschedule.every().monday.at("10:00").do(lambda: asyncio.create_task(send_weekly_report()))

    print("✅ Сервис напоминаний запущен")
    print("📅 Расписание:")
    print("   - Ежедневно в 09:00: отправка напоминаний")
    print("   - Каждый понедельник в 10:00: недельный отчет")

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(60)  # Проверяем каждую минуту


async def send_weekly_report():
    """Еженедельный отчет"""
    from database import get_all_patients, get_patients_due_for_visit

    patients = await get_all_patients()
    due_patients = await get_patients_due_for_visit(7)  # На неделю вперед

    registered = sum(1 for p in patients if p.get('chat_id'))
    due_count = len(due_patients)

    print(f"📊 Еженедельный отчет:")
    print(f"   - Всего пациентов в базе: {len(patients)}")
    print(f"   - Зарегистрировано в боте: {registered}")
    print(f"   - Предстоящие визиты (7 дней): {due_count}")
    print(f"   - Не зарегистрировано: {len(patients) - registered}")


async def manual_send_reminders():
    """Ручной запуск отправки напоминаний (для тестирования)"""
    print("🔔 Ручной запуск отправки напоминаний...")
    count = await send_daily_reminders()
    print(f"✅ Ручная отправка завершена. Отправлено: {count} сообщений")


if __name__ == "__main__":
    # Для запуска отдельного сервиса напоминаний
    print("🚀 Запуск сервиса напоминаний...")
    asyncio.run(start_reminder_service())