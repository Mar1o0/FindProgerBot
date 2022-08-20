from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

client_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
client_menu_kb.add(
	KeyboardButton("Добавить задачу"),
	KeyboardButton("Проверить задачи")
)

client_add_task_inb = InlineKeyboardMarkup()
client_add_task_inb.add(
	InlineKeyboardButton("Выбрать исполнителя", callback_data="select_executor")
)

client_check_tasks_inb = InlineKeyboardMarkup()
client_check_tasks_inb.add(
	InlineKeyboardButton("Список активных задач", callback_data="list_active_tasks")
)