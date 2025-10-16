import asyncio
from database import load_patients, find_patient_by_username


async def check_database():
    """Проверка базы данных"""
    print("🔍 Проверка базы данных...")

    patients = await load_patients()
    print(f"📊 Всего пациентов: {len(patients)}")

    for patient in patients:
        print(f"\n👤 Пациент ID: {patient['id']}")
        print(f"   ФИО: {patient['full_name']}")
        print(f"   Username: {patient.get('telegram_username', 'не указан')}")
        print(f"   Диагноз: {patient['diagnosis']}")
        print(f"   Chat ID: {patient.get('chat_id', 'не установлен')}")

    # Проверим поиск по вашему username
    test_username = "@timshaxx"  # Замените на ваш реальный username
    print(f"\n🔍 Тестируем поиск по username: {test_username}")
    found_patient = await find_patient_by_username(test_username)

    if found_patient:
        print(f"✅ Найден: {found_patient['full_name']} (ID: {found_patient['id']})")
    else:
        print(f"❌ Не найден")


if __name__ == "__main__":
    asyncio.run(check_database())