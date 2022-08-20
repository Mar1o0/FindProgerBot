from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

executors_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
executors_menu_kb.add(
	KeyboardButton("Профиль"),
	KeyboardButton("Список задач")
)

executors_profile_inb = InlineKeyboardMarkup()
executors_profile_inb.add(
	InlineKeyboardButton("Редактировать", callback_data="edit_profile_executor")
).add(
	InlineKeyboardButton("Посмотреть выполненные задачи", callback_data="view_completed_tasks")
)

executors_list_task_inb = InlineKeyboardMarkup()
executors_list_task_inb.add(
	InlineKeyboardButton("Выбрать задачу", callback_data="select_task")
)
