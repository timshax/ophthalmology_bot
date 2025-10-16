from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from database import find_patient_by_chat_id
from config import MESSAGE_TEMPLATES

router = Router()


def get_registration_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Зарегистрироваться")]
        ],
        resize_keyboard=True
    )


@router.message(lambda message: message.text == "📋 Мои данные")
async def show_my_data(message: types.Message):
    """Показать данные пациента"""
    patient = await find_patient_by_chat_id(message.chat.id)

    if patient:
        diagnosis_info = MESSAGE_TEMPLATES.get(patient['diagnosis'], {})
        educational = diagnosis_info.get('educational', '')

        response = (
            f"👤 <b>Ваши данные:</b>\n"
            f"• ФИО: {patient['full_name']}\n"
            f"• Telegram: {patient.get('telegram_username', 'не указан')}\n"
            f"• Диагноз: {patient['diagnosis']}\n"
            f"• Следующий визит: {patient['next_visit']}\n\n"
            f"{educational}"
        )
        await message.answer(response, parse_mode='HTML')
    else:
        await message.answer(
            "❌ Вы не зарегистрированы в системе. Напишите /start для регистрации.",
            reply_markup=get_registration_keyboard()
        )


@router.message(lambda message: message.text == "📅 Ближайший визит")
async def show_next_visit(message: types.Message):
    """Информация о ближайшем визите"""
    patient = await find_patient_by_chat_id(message.chat.id)

    if patient:
        template = MESSAGE_TEMPLATES.get(patient['diagnosis'], {}).get('reminder',
                                                                       "Напоминание о визите {visit_date} для пациента {name}.")

        reminder_text = template.format(
            name=patient['full_name'],
            visit_date=patient['next_visit']
        )

        await message.answer(reminder_text)
    else:
        await message.answer(
            "❌ Вы не зарегистрированы в системе. Напишите /start для регистрации.",
            reply_markup=get_registration_keyboard()
        )


@router.message(lambda message: message.text == "ℹ️ Обучение")
async def show_education(message: types.Message):
    """Показать обучающую информацию"""
    patient = await find_patient_by_chat_id(message.chat.id)

    if patient:
        educational = MESSAGE_TEMPLATES.get(patient['diagnosis'], {}).get('educational',
                                                                          "Регулярные осмотры важны для сохранения здоровья ваших глаз.")

        await message.answer(educational)
    else:
        await message.answer(
            "❌ Вы не зарегистрированы в системе. Напишите /start для регистрации.",
            reply_markup=get_registration_keyboard()
        )