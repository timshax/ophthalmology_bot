from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database import find_patient_by_username, update_patient_chat_id, get_all_patients
from config import MESSAGE_TEMPLATES

router = Router()



def get_main_keyboard():
    """Клавиатура для главного меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Мои данные")],
            [KeyboardButton(text="📅 Ближайший визит")],
            [KeyboardButton(text="ℹ️ Обучение")],
            [KeyboardButton(text="👥 Админ: Список пациентов")]
        ],
        resize_keyboard=True
    )
    print("🔄 Создана главная клавиатура")  # Отладочное сообщение
    return keyboard


def get_registration_keyboard():
    """Клавиатура для регистрации"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Зарегистрироваться")]
        ],
        resize_keyboard=True
    )
    print("🔄 Создана клавиатура регистрации")  # Отладочное сообщение
    return keyboard


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""

    username = message.from_user.username
    print(f"🔍 Пользователь {message.from_user.full_name} пытается зарегистрироваться с username: {username}")

    if not username:
        keyboard = get_registration_keyboard()
        print("❌ Username не установлен, показываю клавиатуру регистрации")
        await message.answer(
            "❌ У вас не установлен username в Telegram. "
            "Пожалуйста, установите username в настройках Telegram и попробуйте снова.",
            reply_markup=keyboard
        )
        return

    telegram_username = f"@{username}"
    patient = await find_patient_by_username(telegram_username)

    if patient:
        await update_patient_chat_id(patient['id'], message.chat.id)

        keyboard = get_main_keyboard()
        print(f"✅ Пользователь {patient['full_name']} найден, показываю главную клавиатуру")

        await message.answer(
            f"✅ Добро пожаловать, {patient['full_name']}!\n"
            f"Я ваш ассистент для напоминаний о визитах к офтальмологу.",
            reply_markup=keyboard
        )
        print(f"✅ Сообщение с клавиатурой отправлено для {patient['full_name']}")
    else:
        all_patients = await get_all_patients()
        available_usernames = [p.get('telegram_username', 'не указан') for p in all_patients]

        keyboard = get_registration_keyboard()
        print(f"❌ Username {telegram_username} не найден, показываю клавиатуру регистрации")

        await message.answer(
            f"❌ Пользователь {telegram_username} не найден в базе пациентов.\n\n"
            f"Доступные username в базе:\n" + "\n".join(available_usernames) + "\n\n"
                                                                               "Если вы пациент, обратитесь к администратору для добавления в систему.",
            reply_markup=keyboard
        )


@router.message(lambda message: message.text == "📝 Зарегистрироваться")
async def register_again(message: types.Message):
    """Повторная попытка регистрации"""
    print("🔄 Повторная регистрация")
    await cmd_start(message)


@router.message(Command("test_keyboard"))
async def cmd_test_keyboard(message: types.Message):
    """Тестовая команда для проверки клавиатуры"""
    print("🔧 Тестируем клавиатуру")
    keyboard = get_main_keyboard()
    await message.answer(
        "Тест клавиатуры - должны быть видны кнопки:",
        reply_markup=keyboard
    )


@router.message(Command("debug"))
async def cmd_debug(message: types.Message):
    """Команда для отладки"""
    username = message.from_user.username
    all_patients = await get_all_patients()
    current_patient = await find_patient_by_username(f"@{username}") if username else None

    debug_info = (
        f"👤 Ваш username: @{username if username else 'не установлен'}\n"
        f"🔍 Ваш chat_id: {message.chat.id}\n"
        f"📊 Всего пациентов в базе: {len(all_patients)}\n"
        f"✅ Вы в базе: {'ДА' if current_patient else 'НЕТ'}\n"
        f"🔍 Доступные username:\n"
    )

    for patient in all_patients:
        status = "✅" if patient.get('chat_id') else "❌"
        debug_info += f"{status} {patient.get('telegram_username', 'не указан')} - {patient['full_name']}\n"

    await message.answer(debug_info)