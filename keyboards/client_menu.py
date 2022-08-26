from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

client_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
client_menu_kb.add(
	KeyboardButton("📝 Добавить задачу 📝"),
	KeyboardButton("👁 Список активных задач 👁")
)

client_check_tasks_inb = InlineKeyboardMarkup()
client_check_tasks_inb.add(
	InlineKeyboardButton("Список активных задач", callback_data="list_active_tasks")
)

info_about_task = InlineKeyboardMarkup()
info_about_task.add(
	InlineKeyboardButton("Изменить краткое название", callback_data="edit_short_name"),
	InlineKeyboardButton("Изменить описание", callback_data="edit_description"),
	InlineKeyboardButton("Изменить дедлайн", callback_data="edit_deadline"),
	InlineKeyboardButton("Удалить задачу", callback_data="delete_task")
)

delete_task_inb = InlineKeyboardMarkup()
delete_task_inb.add(
	InlineKeyboardButton("✅", callback_data="yes"),
	InlineKeyboardButton("❌", callback_data="no")
)
