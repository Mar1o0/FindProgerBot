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

select_task_executor = InlineKeyboardMarkup()
select_task_executor.add(
	InlineKeyboardButton("Изменить статус", callback_data='edit_status'),
	InlineKeyboardButton("Начать выполнение", callback_data='start_execution')
).add(
	InlineKeyboardButton("🏁 Завершить задачу 🏁", callback_data='finish_task')
)

timer_start = InlineKeyboardMarkup()
timer_start.add(
	InlineKeyboardButton("🟢 Запустить счетчик времени 🟢", callback_data="timer_start")
)

timer_stop = InlineKeyboardMarkup()
timer_stop.add(
	InlineKeyboardButton("🔴 Остановить счетчик времени 🔴", callback_data="timer_stop")
)

status_notice_inb = InlineKeyboardMarkup()
status_notice_inb.add(
	InlineKeyboardButton("Прочитано 👀", callback_data="status_read_notice")
).add(
	InlineKeyboardButton("Отменено ⛔️", callback_data="status_canceled_notice")
)

receipt_button = InlineKeyboardMarkup()
receipt_button.add(
	InlineKeyboardButton("💰 Подтвердить чек 💰", callback_data="send_receipt")
).add(
	InlineKeyboardButton("Отредактировать чек", callback_data="edit_receipt")
)

edit_receipt = InlineKeyboardMarkup()
edit_receipt.add(
	InlineKeyboardButton("Добавить описание", callback_data="add_description"),
	InlineKeyboardButton("Изменить сумму", callback_data="edit_final_price")
)
