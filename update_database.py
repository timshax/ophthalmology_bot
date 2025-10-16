import asyncio
from database import save_patients, INITIAL_PATIENTS_DATA


async def reset_database():
    """Сброс базы данных к начальному состоянию"""
    print("🔄 Сброс базы данных...")

    # Очищаем chat_id у всех пациентов
    for patient in INITIAL_PATIENTS_DATA:
        patient['chat_id'] = None

    await save_patients(INITIAL_PATIENTS_DATA)
    print("✅ База данных сброшена!")


async def add_new_patient():
    """Добавление нового пациента"""
    new_patient = {
        "id": 5,  # Убедитесь что ID уникальный
        "full_name": "Ваше ФИО",  # Замените на реальное
        "telegram_username": "@timshaxx",  # Замените на ваш реальный username
        "diagnosis": "глаукома",  # Или другой диагноз
        "next_visit": "2024-12-30",
        "chat_id": None
    }

    patients = await load_patients()
    patients.append(new_patient)
    await save_patients(patients)
    print(f"✅ Добавлен новый пациент: {new_patient['full_name']}")


if __name__ == "__main__":
    # Запустите нужную функцию
    asyncio.run(reset_database())
    # или
    # asyncio.run(add_new_patient())