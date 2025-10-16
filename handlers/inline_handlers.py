from aiogram import Router, types
from aiogram.filters import Command

from database import find_patient_by_chat_id, find_patient_by_username, update_patient_chat_id, get_all_patients
from config import MESSAGE_TEMPLATES
from keyboards import get_main_inline_keyboard, get_registration_inline_keyboard  # Импорт из пакета keyboards

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start с inline-кнопками"""

    username = message.from_user.username
    print(f"🔍 Inline: Пользователь {message.from_user.full_name} с username: {username}")

    if not username:
        keyboard = get_registration_inline_keyboard()
        await message.answer(
            "❌ У вас не установлен username в Telegram.\n\n"
            "Пожалуйста, установите username в настройках Telegram и нажмите кнопку ниже:",
            reply_markup=keyboard
        )
        return

    telegram_username = f"@{username}"
    patient = await find_patient_by_username(telegram_username)

    # ОТЛАДОЧНАЯ ИНФОРМАЦИЯ
    all_patients = await get_all_patients()
    print(f"🔍 Все пациенты в базе:")
    for p in all_patients:
        print(f"   ID: {p['id']}, Username: {p.get('telegram_username')}, Name: {p['full_name']}")

    print(f"🔍 Ищем: {telegram_username}")
    print(f"🔍 Найден пациент: {patient}")

    if patient:
        await update_patient_chat_id(patient['id'], message.chat.id)

        keyboard = get_main_inline_keyboard()
        await message.answer(
            f"✅ Добро пожаловать, {patient['full_name']}!\n\n"
            f"Я ваш ассистент для напоминаний о визитах к офтальмологу.\n\n"
            f"📋 <b>Ваш диагноз:</b> {patient['diagnosis']}\n"
            f"📅 <b>Следующий визит:</b> {patient['next_visit']}\n\n"
            f"Выберите действие:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        print(f"✅ Inline: Пользователь {patient['full_name']} (ID: {patient['id']}) зарегистрирован")
    else:
        keyboard = get_registration_inline_keyboard()
        await message.answer(
            f"❌ Пользователь {telegram_username} не найден в базе пациентов.\n\n"
            "Если вы пациент, обратитесь к администратору для добавления в систему.",
            reply_markup=keyboard
        )


@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    """Показать inline-меню"""
    keyboard = get_main_inline_keyboard()
    await message.answer(
        "📱 <b>Главное меню:</b>\n\nВыберите действие:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )


@router.message(Command("debug"))
async def cmd_debug(message: types.Message):
    """Отладочная информация"""
    username = message.from_user.username
    all_patients = await get_all_patients()
    current_patient = await find_patient_by_username(f"@{username}") if username else None

    debug_info = (
        f"👤 <b>Отладочная информация:</b>\n\n"
        f"• <b>Ваш username:</b> @{username if username else 'не установлен'}\n"
        f"• <b>Chat ID:</b> {message.chat.id}\n"
        f"• <b>Всего пациентов:</b> {len(all_patients)}\n"
        f"• <b>Вы в базе:</b> {'✅ ДА' if current_patient else '❌ НЕТ'}\n\n"
        f"<b>Доступные username:</b>\n"
    )

    for patient in all_patients:
        status = "✅" if patient.get('chat_id') else "❌"
        debug_info += f"{status} {patient.get('telegram_username', 'не указан')} - {patient['full_name']}\n"

    await message.answer(debug_info, parse_mode='HTML')


# Обработчики callback-запросов для inline-кнопок
@router.callback_query(lambda c: c.data == "my_data")
async def process_my_data(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Мои данные'"""
    patient = await find_patient_by_chat_id(callback_query.from_user.id)

    if patient:
        diagnosis_info = MESSAGE_TEMPLATES.get(patient['diagnosis'], {})
        educational = diagnosis_info.get('educational', '')

        response = (
            f"👤 <b>Ваши данные:</b>\n\n"
            f"• <b>ФИО:</b> {patient['full_name']}\n"
            f"• <b>Telegram:</b> {patient.get('telegram_username', 'не указан')}\n"
            f"• <b>Диагноз:</b> {patient['diagnosis']}\n"
            f"• <b>Следующий визит:</b> {patient['next_visit']}\n\n"
            f"{educational}"
        )
    else:
        response = "❌ Вы не зарегистрированы в системе. Напишите /start"

    await callback_query.message.answer(response, parse_mode='HTML')
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "next_visit")
async def process_next_visit(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Ближайший визит'"""
    patient = await find_patient_by_chat_id(callback_query.from_user.id)

    if patient:
        template = MESSAGE_TEMPLATES.get(patient['diagnosis'], {}).get('reminder',
                                                                       "Напоминание о визите {visit_date} для пациента {name}.")

        reminder_text = template.format(
            name=patient['full_name'],
            visit_date=patient['next_visit']
        )
        response = reminder_text
    else:
        response = "❌ Вы не зарегистрированы в системе. Напишите /start"

    await callback_query.message.answer(response)
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "education")
async def process_education(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Обучение'"""
    patient = await find_patient_by_chat_id(callback_query.from_user.id)

    if patient:
        educational = MESSAGE_TEMPLATES.get(patient['diagnosis'], {}).get('educational',
                                                                          "Регулярные осмотры важны для сохранения здоровья ваших глаз.")
        response = educational
    else:
        response = "❌ Вы не зарегистрированы в системе. Напишите /start"

    await callback_query.message.answer(response)
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "admin_list")
async def process_admin_list(callback_query: types.CallbackQuery):
    """Обработчик кнопки 'Список пациентов'"""
    patients = await get_all_patients()

    response = "👥 <b>Все пациенты:</b>\n\n"
    for patient in patients:
        status = "✅ Зарегистрирован" if patient.get('chat_id') else "❌ Не в боте"
        response += (
            f"• <b>{patient['full_name']}</b>\n"
            f"  👤 {patient.get('telegram_username', 'не указан')}\n"
            f"  🏥 {patient['diagnosis']}\n"
            f"  📅 {patient['next_visit']}\n"
            f"  📊 {status}\n\n"
        )

    await callback_query.message.answer(response, parse_mode='HTML')
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "refresh_menu")
async def process_refresh_menu(callback_query: types.CallbackQuery):
    """Обновить меню"""
    keyboard = get_main_inline_keyboard()
    await callback_query.message.edit_text(
        "📱 <b>Главное меню обновлено:</b>\n\nВыберите действие:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    await callback_query.answer("Меню обновлено!")


@router.callback_query(lambda c: c.data == "register")
async def process_register(callback_query: types.CallbackQuery):
    """Обработчик кнопки регистрации"""
    await cmd_start(callback_query.message)
    await callback_query.answer()


@router.callback_query(lambda c: c.data == "retry_register")
async def process_retry_register(callback_query: types.CallbackQuery):
    """Повторная попытка регистрации"""
    await cmd_start(callback_query.message)
    await callback_query.answer()