from aiogram import Router, types
from database import get_all_patients

router = Router()


@router.message(lambda message: message.text == "👥 Админ: Список пациентов")
async def show_all_patients(message: types.Message):
    """Админская функция: показать всех пациентов"""
    patients = await get_all_patients()

    response = "👥 <b>Все пациенты:</b>\n\n"
    for patient in patients:
        status = "✅ Зарегистрирован" if patient.get('chat_id') else "❌ Не в боте"
        response += (
            f"• {patient['full_name']}\n"
            f"  Telegram: {patient.get('telegram_username', 'не указан')}\n"
            f"  Диагноз: {patient['diagnosis']}\n"
            f"  Визит: {patient['next_visit']}\n"
            f"  Статус: {status}\n\n"
        )

    await message.answer(response, parse_mode='HTML')