import json
import aiofiles
import os
from datetime import datetime, timedelta
from config import DATABASE_FILE, MESSAGE_TEMPLATES
from aiogram import Bot
from config import BOT_TOKEN

# Создаем папку data если её нет
os.makedirs("data", exist_ok=True)

# Начальные данные пациентов
INITIAL_PATIENTS_DATA = [
    {
        "id": 1,
        "full_name": "Афанасьев Артем",
        "telegram_username": "@NataliaMorina",
        "diagnosis": "глаукома",
        "next_visit": "2024-12-15",
        "chat_id": None
    },
    {
        "id": 2,
        "full_name": "Афанасьев Артем",
        "telegram_username": "@freilakh",
        "diagnosis": "катаракта",
        "next_visit": "2024-12-20",
        "chat_id": None
    },
    {
        "id": 3,
        "full_name": "Сидоров Алексей Владимирович",
        "telegram_username": "@sqrtchel",
        "diagnosis": "глаукома",
        "next_visit": "2024-11-30",
        "chat_id": None
    },
    {
        "id": 4,
        "full_name": "Козлова Алина Сергеевна",
        "telegram_username": "@timshaxx",
        "diagnosis": "катаракта",
        "next_visit": "2024-12-25",
        "chat_id": None
    },
    {
        "id": 5,
        "full_name": "Козлова Мария Сергеевна",
        "telegram_username": "@desperado129",
        "diagnosis": "катаракта",
        "next_visit": "2024-12-25",
        "chat_id": None
    }


]

# Добавьте эту функцию в database.py
async def get_patients_debug_info():
    """Получить отладочную информацию о пациентах"""
    patients = await load_patients()
    info = []
    for patient in patients:
        info.append({
            'id': patient['id'],
            'name': patient['full_name'],
            'username': patient.get('telegram_username', 'не указан'),
            'chat_id': patient.get('chat_id'),
            'registered': bool(patient.get('chat_id'))
        })
    return info

async def init_database():
    """Инициализация базы данных"""
    if not os.path.exists(DATABASE_FILE):
        await save_patients(INITIAL_PATIENTS_DATA)
        print("✅ База данных инициализирована!")


async def load_patients():
    """Асинхронная загрузка данных пациентов"""
    try:
        async with aiofiles.open(DATABASE_FILE, 'r', encoding='utf-8') as f:
            data = await f.read()
            return json.loads(data)
    except FileNotFoundError:
        return INITIAL_PATIENTS_DATA
    except json.JSONDecodeError:
        print("❌ Ошибка чтения базы данных, возвращаю начальные данные")
        return INITIAL_PATIENTS_DATA


async def save_patients(patients):
    """Асинхронное сохранение данных пациентов"""
    async with aiofiles.open(DATABASE_FILE, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(patients, ensure_ascii=False, indent=2))


async def find_patient_by_username(username):
    """Поиск пациента по телеграм username"""
    patients = await load_patients()

    username_lower = username.lower().lstrip('@')
    print(f"🔍 Поиск пациента по username: '{username}' -> '{username_lower}'")  # Отладка

    for patient in patients:
        patient_username = patient.get('telegram_username', '').lower().lstrip('@')
        print(f"🔍 Сравниваем с: '{patient_username}'")  # Отладка

        if patient_username == username_lower:
            print(f"✅ Найден пациент: {patient['full_name']} (ID: {patient['id']})")
            return patient

    print(f"❌ Пациент с username '{username}' не найден")
    return None

async def find_patient_by_chat_id(chat_id):
    """Поиск пациента по chat_id"""
    patients = await load_patients()
    for patient in patients:
        if patient.get('chat_id') == chat_id:
            return patient
    return None


async def update_patient_chat_id(patient_id, chat_id):
    """Обновление chat_id пациента"""
    patients = await load_patients()
    for patient in patients:
        if patient['id'] == patient_id:
            patient['chat_id'] = chat_id
            break
    await save_patients(patients)


async def get_patients_due_for_visit(days_ahead=30):
    """Поиск пациентов, которым визит нужен в течение указанных дней"""
    patients = await load_patients()
    today = datetime.now().date()
    target_date = today + timedelta(days=days_ahead)

    due_patients = []

    for patient in patients:
        try:
            visit_date = datetime.strptime(patient['next_visit'], '%Y-%m-%d').date()
            if today <= visit_date <= target_date:
                due_patients.append(patient)
        except ValueError:
            continue

    return due_patients


async def get_all_patients():
    """Получение всех пациентов"""
    return await load_patients()


async def send_reminders(bot: Bot):
    """Функция для отправки напоминаний"""
    due_patients = await get_patients_due_for_visit(30)

    sent_count = 0
    for patient in due_patients:
        if patient.get('chat_id'):
            template = MESSAGE_TEMPLATES.get(patient['diagnosis'], {}).get('reminder',
                                                                           "Напоминание о визите {visit_date} для пациента {name}.")

            reminder_text = template.format(
                name=patient['full_name'],
                visit_date=patient['next_visit']
            )

            try:
                await bot.send_message(
                    chat_id=patient['chat_id'],
                    text=reminder_text
                )
                print(f"✅ Напоминание отправлено: {patient['full_name']} ({patient.get('telegram_username')})")
                sent_count += 1
                await asyncio.sleep(1)  # Пауза между отправками
            except Exception as e:
                print(f"❌ Ошибка отправки {patient['full_name']}: {e}")

    return sent_count