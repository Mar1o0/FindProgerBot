from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

executors_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
executors_menu_kb.add(
	KeyboardButton("👤 Профиль 👤"),
	KeyboardButton("📚 Список задач 📚")
)

executors_profile_inb = InlineKeyboardMarkup()
executors_profile_inb.add(
	InlineKeyboardButton("Редактировать", callback_data="edit_profile_executor")
).add(
	InlineKeyboardButton("📚 Посмотреть выполненные задачи", callback_data="view_completed_tasks")
)

notice_edit_status = InlineKeyboardMarkup()
notice_edit_status.add(
	InlineKeyboardButton("Прочитано 👀", callback_data="notice_status_read"),
	InlineKeyboardButton("Начал выполнение ✏️", callback_data="notice_status_start"),
	InlineKeyboardButton("Выполнено ✅", callback_data="notice_status_success"),
	InlineKeyboardButton("Отменено ⛔️", callback_data="notice_status_canceled")
)

edit_status = InlineKeyboardMarkup()
edit_status.add(
	InlineKeyboardButton("Прочитано 👀", callback_data="status_read"),
	InlineKeyboardButton("Начал выполнение ✏️", callback_data="status_start"),
	InlineKeyboardButton("Выполнено ✅", callback_data="status_success"),
	InlineKeyboardButton("Отменено ⛔️", callback_data="status_canceled")
)

edit_profile_executor = InlineKeyboardMarkup()
edit_profile_executor.add(
	InlineKeyboardButton("Изменить имя", callback_data='rename_executor'),
	InlineKeyboardButton("Изменить ставку", callback_data='set_stake')
)
