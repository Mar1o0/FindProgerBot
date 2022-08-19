from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

executors_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
executors_menu_kb.add(
	KeyboardButton("Профиль"),
	KeyboardButton("Список задач")
)
