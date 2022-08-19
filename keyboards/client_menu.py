from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

client_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
client_menu_kb.add(
	KeyboardButton("Добавить задачу"),
	KeyboardButton("Проверить задачи")
)
