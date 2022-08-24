from aiogram import types, Dispatcher
import sqlite3
from keyboards import executors_menu as em
from handlers import functions as func
from create_bot import bot
from handlers import client
from aiogram.dispatcher.filters import Text

call_active_tasks_executor = None


async def handler_executors(message: types.Message):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	access_id = cursor.execute(f"SELECT access_id FROM users WHERE tg_id == {message.from_user.id}").fetchone()
	if access_id[0] == 10:
		await message.answer("Вы перешли в меню \"Исполнитель\"", reply_markup=em.executors_menu_kb)


async def profile(message: types.Message):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	access_id = cursor.execute(f"SELECT access_id FROM users WHERE tg_id == {message.from_user.id}").fetchone()[0]
	name = cursor.execute(f"SELECT name FROM users WHERE tg_id == {message.from_user.id}").fetchone()
	stake = cursor.execute(f"SELECT stake FROM users WHERE tg_id == {message.from_user.id}").fetchone()
	if access_id == 10:
		await message.answer(f"<b>Имя:</b> {name[0]}\n<b>Ставка:</b> {stake[0]}$/час", reply_markup=em.executors_profile_inb, parse_mode="HTML")


async def list_task(message: types.Message):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	access_id = cursor.execute(f"SELECT access_id FROM users WHERE tg_id == {message.from_user.id}").fetchone()[0]
	if access_id == 10:
		data_tasks = cursor.execute('SELECT * FROM tasks WHERE executor_id = ? AND status != "Выполнено ✅"', [message.from_user.id]).fetchall()
		a = []
		if data_tasks == a:
			await message.answer("Список задач пуст")
		else:
			await message.answer("Список активных задач", reply_markup=func.check_active_tasks_for_executor(data_tasks))


async def callback_handler_executors(callback: types.CallbackQuery):
	if callback.data == "edit_profile_executor":
		await callback.answer()
		await callback.message.delete()
		await callback.message.answer("Выберите что хотите изменить", reply_markup=em.edit_profile_executor)

	# Обработать ошибку если тут пусто
	if callback.data == "view_completed_tasks":
		conn = sqlite3.connect('base.db')
		cursor = conn.cursor()
		all_completed_tasks = cursor.execute("SELECT short_name, final_price, timer FROM tasks WHERE executor_id = ? AND status = ?", [callback.from_user.id, "Выполнено ✅"]).fetchall()
		await callback.answer()
		await callback.message.delete()
		text = ""
		a = []
		if not all_completed_tasks == a:
			for i in all_completed_tasks:
				text += f"Название: {i[0]}\nСумма: {i[1]}$ за {i[2]} час(-ов)\n\n"
		else:
			text = "Список выполненных задач пуст"
		await callback.message.answer(text)

	if callback.data == "rename_executor":
		await callback.answer()
		await callback.message.delete()
		await func.FSMEditNameInProfile.new_name.set()
		await callback.message.answer("Введите новое имя")

	if callback.data == "set_stake":
		await callback.answer()
		await callback.message.delete()
		await func.FSMEditStakeExecutor.new_stake.set()
		await callback.message.answer("Введите ставку")


async def callback_check_active_tasks_for_executor(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	global call_active_tasks_executor
	call_active_tasks_executor = int(callback.data.split("_")[1])
	await callback.answer()
	await callback.message.delete()
	short_name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
	description = cursor.execute(f'SELECT description FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
	deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
	status = cursor.execute(f'SELECT status FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
	client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
	client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
	await callback.message.answer(
		f"<b>Краткое название:</b> {short_name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status}\n<b>Клиент:</b> {client_login}({client_id})",
		reply_markup=em.edit_status, parse_mode='HTML')


async def callback_edit_status(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()

	if callback.data == "status_read":
		await callback.answer()
		await callback.message.delete()
		if call_active_tasks_executor is None:
			plug = cursor.execute(f"SELECT tg_id FROM users WHERE id = {client.call_add_task}").fetchone()[0]
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			description = cursor.execute(f'SELECT description FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			client_login = cursor.execute(f'SELECT client FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Прочитано 👀', name])
			conn.commit()
			status_read = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
			await callback.message.answer(
				f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_read}\n<b>Клиент:</b> {client_login}({client_id})",
				reply_markup=em.edit_status, parse_mode='HTML')
		else:
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			description = cursor.execute(f'SELECT description FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Прочитано 👀', name])
			conn.commit()
			status_read = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
			await callback.message.answer(
				f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_read}\n<b>Клиент:</b> {client_login}({client_id})",
				reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "status_start":
		await callback.answer()
		await callback.message.delete()
		if call_active_tasks_executor is None:
			plug = cursor.execute(f"SELECT tg_id FROM users WHERE id = {client.call_add_task}").fetchone()[0]
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			description = cursor.execute(f'SELECT description FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			client_login = cursor.execute(f'SELECT client FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Начал выполнение ✏️', name])
			conn.commit()
			status_start = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
			await callback.message.answer(
				f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_start}\n<b>Клиент:</b> {client_login}({client_id})",
				reply_markup=em.edit_status, parse_mode='HTML')
		else:
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			description = cursor.execute(f'SELECT description FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Начал выполнение ✏️', name])
			conn.commit()
			status_start = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
			await callback.message.answer(
				f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_start}\n<b>Клиент:</b> {client_login}({client_id})",
				reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "status_success":
		await callback.answer()
		await callback.message.delete()
		if call_active_tasks_executor is None:
			plug = cursor.execute(f"SELECT tg_id FROM users WHERE id = {client.call_add_task}").fetchone()[0]
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			description = cursor.execute(f'SELECT description FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			client_login = cursor.execute(f'SELECT client FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Выполнено ✅', name])
			conn.commit()
			status_success = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
			await callback.message.answer(
				f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_success}\n<b>Клиент:</b> {client_login}({client_id})",
				reply_markup=em.edit_status, parse_mode='HTML')
		else:
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			description = cursor.execute(f'SELECT description FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Выполнено ✅', name])
			conn.commit()
			status_success = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
			await callback.message.answer(
				f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_success}\n<b>Клиент:</b> {client_login}({client_id})",
				reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "status_canceled":
		await callback.answer()
		await callback.message.delete()
		if call_active_tasks_executor is None:
			plug = cursor.execute(f"SELECT tg_id FROM users WHERE id = {client.call_add_task}").fetchone()[0]
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE executor_id = {plug}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Отменено ⛔️', name])
			conn.commit()
			chat_id = cursor.execute("SELECT client_id FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
			executor_name = cursor.execute("SELECT executor FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
			await bot.send_message(chat_id, f"Выша задача с названием <b>\"{name}\"</b> была отменена исполнителем <b>{executor_name}</b>. "
			                                f"Измените название/описание/дедлайн и попробуйте создать задачу еще раз.", parse_mode="HTML")
			cursor.execute("DELETE FROM tasks WHERE short_name = ?", [name])
			conn.commit()
		else:
			name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_active_tasks_executor}').fetchone()[0]
			cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Отменено ⛔️', name])
			conn.commit()
			chat_id = cursor.execute("SELECT client_id FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
			executor_name = cursor.execute("SELECT executor FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
			await bot.send_message(chat_id, f"Выша задача с названием <b>\"{name}\"</b> была отменена исполнителем <b>{executor_name}</b>. "
			                                f"Измените название/описание/дедлайн и попробуйте создать задачу еще раз.", parse_mode="HTML")
			cursor.execute("DELETE FROM tasks WHERE short_name = ?", [name])
			conn.commit()


async def callback_notice_edit_status(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	if callback.data == "notice_status_read":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		description = cursor.execute(f'SELECT description FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Прочитано 👀', name])
		conn.commit()
		status_read = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
		await callback.message.answer(
			f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_read}\n<b>Клиент:</b> {client_login}({client_id})",
			reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "notice_status_start":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		description = cursor.execute(f'SELECT description FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Начал выполнение ✏️', name])
		conn.commit()
		status_start = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
		await callback.message.answer(
			f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_start}\n<b>Клиент:</b> {client_login}({client_id})",
			reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "notice_status_success":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		description = cursor.execute(f'SELECT description FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Выполнено ✅', name])
		conn.commit()
		status_success = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
		await callback.message.answer(
			f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status_success}\n<b>Клиент:</b> {client_login}({client_id})",
			reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "notice_status_canceled":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Отменено ⛔️', name])
		conn.commit()
		chat_id = cursor.execute("SELECT client_id FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
		executor_name = cursor.execute("SELECT executor FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
		await bot.send_message(chat_id, f"Выша задача с названием <b>\"{name}\"</b> была отменена исполнителем <b>{executor_name}</b>. "
		                                f"Измените название/описание/дедлайн и попробуйте создать задачу еще раз.", parse_mode="HTML")
		cursor.execute("DELETE FROM tasks WHERE short_name = ?", [name])
		conn.commit()


def register_handler_executors(dp: Dispatcher):
	dp.register_message_handler(handler_executors, commands=["admin"])
	dp.register_message_handler(profile, text=["👤 Профиль 👤"])
	dp.register_message_handler(list_task, text=["📚 Список задач 📚"])
	dp.register_callback_query_handler(callback_handler_executors, text=["edit_profile_executor", "view_completed_tasks",
	                                                                     "rename_executor", "set_stake"])
	dp.register_callback_query_handler(callback_check_active_tasks_for_executor,
	                                   Text(startswith='active-tasks_'))
	dp.register_callback_query_handler(callback_edit_status, text=["status_read", "status_start",
	                                                               "status_success", "status_canceled"])
	dp.register_callback_query_handler(callback_notice_edit_status, text=["notice_status_read", "notice_status_start",
	                                                                      "notice_status_success", "notice_status_canceled"])
