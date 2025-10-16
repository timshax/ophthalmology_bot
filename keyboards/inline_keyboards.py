from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_inline_keyboard():
    """Inline-клавиатура для главного меню"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои данные", callback_data="my_data")],
            [InlineKeyboardButton(text="📅 Ближайший визит", callback_data="next_visit")],
            [InlineKeyboardButton(text="ℹ️ Обучение", callback_data="education")],
            [InlineKeyboardButton(text="👥 Админ: Список пациентов", callback_data="admin_list")],
            [InlineKeyboardButton(text="🔄 Обновить меню", callback_data="refresh_menu")]
        ]
    )
    return keyboard

def get_registration_inline_keyboard():
    """Inline-клавиатура для регистрации"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Зарегистрироваться", callback_data="register")],
            [InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="retry_register")]
        ]
    )
    return keyboard