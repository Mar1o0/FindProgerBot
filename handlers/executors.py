from aiogram import types, Dispatcher
import sqlite3
import datetime
from keyboards import executors_menu as em
from handlers import functions as func
from create_bot import bot
from aiogram.dispatcher.filters import Text

call_active_tasks_executor = None
timer_start = False
start_time = ""


def looking_data_in_table(data):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	short_name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {data}').fetchone()[0]
	description = cursor.execute(f'SELECT description FROM tasks WHERE id = {data}').fetchone()[0]
	deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {data}').fetchone()[0]
	status = cursor.execute(f'SELECT status FROM tasks WHERE id = {data}').fetchone()[0]
	client_login = cursor.execute(f'SELECT client FROM tasks WHERE id = {data}').fetchone()[0]
	client_id = cursor.execute(f'SELECT client_id FROM tasks WHERE id = {data}').fetchone()[0]
	hour = cursor.execute(f'SELECT timer FROM tasks WHERE id = {data}').fetchone()[0]
	executor_name = cursor.execute(f"SELECT executor FROM tasks WHERE id = {data}").fetchone()[0]
	final_price = cursor.execute(f"SELECT final_price FROM tasks WHERE id = {data}").fetchone()[0]
	description_receipt = cursor.execute(f"SELECT description_receipt FROM tasks WHERE id = {data}").fetchone()[0]
	return short_name, description, deadline, status, client_login, client_id, hour, executor_name, final_price, description_receipt


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
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	if callback.data == "edit_profile_executor":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f"SELECT name FROM users WHERE tg_id == {callback.from_user.id}").fetchone()
		stake = cursor.execute(f"SELECT stake FROM users WHERE tg_id == {callback.from_user.id}").fetchone()
		await callback.message.answer(f"<b>Имя:</b> {name[0]}\n<b>Ставка:</b> {stake[0]}$/час", reply_markup=em.edit_profile_executor, parse_mode="HTML")

	if callback.data == "view_completed_tasks":
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
		await callback.message.answer("Введите новое имя\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")

	if callback.data == "set_stake":
		await callback.answer()
		await callback.message.delete()
		await func.FSMEditStakeExecutor.new_stake.set()
		await callback.message.answer("Введите ставку\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")


async def callback_check_active_tasks_for_executor(callback: types.CallbackQuery):
	global call_active_tasks_executor
	call_active_tasks_executor = int(callback.data.split("_")[1])
	await callback.answer()
	await callback.message.delete()
	call = looking_data_in_table(call_active_tasks_executor)
	await callback.message.answer(
		f"<b>Краткое название:</b> {call[0]}\n<b>Описание:</b> {call[1]}\n<b>Дедлайн:</b> {call[2]}\n<b>Статус:</b> {call[3]}\n<b>Клиент:</b> @{call[4]}({call[5]})",
		reply_markup=em.select_task_executor, parse_mode='HTML')


async def callback_select_task_executor(callback: types.CallbackQuery):
	if callback.data == "edit_status":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		await callback.message.answer(
			f"<b>Краткое название:</b> {call[0]}\n<b>Описание:</b> {call[1]}\n<b>Дедлайн:</b> {call[2]}\n<b>Статус:</b> {call[3]}\n<b>Клиент:</b> @{call[4]}({call[5]})",
			reply_markup=em.edit_status, parse_mode='HTML')
		
	if callback.data == "start_execution":
		call = looking_data_in_table(call_active_tasks_executor)
		await callback.answer()
		await callback.message.delete()
		if not timer_start:
			await callback.message.answer(
				f"<b>Краткое название:</b> {call[0]}\n<b>Сколько часов потрачено:</b> {call[6]}",
				reply_markup=em.timer_start, parse_mode='HTML')
		else:
			await callback.message.answer(
				f"<b>Краткое название:</b> {call[0]}\n<b>Сколько часов потрачено:</b> {call[6]}",
				reply_markup=em.timer_stop, parse_mode='HTML')
			
	if callback.data == "finish_task":
		call = looking_data_in_table(call_active_tasks_executor)
		await callback.answer()
		await callback.message.delete()
		if call[9] is None:
			await callback.message.answer(f"<b>Название задачи:</b> {call[0]}\n"
			                              f"<b>Описание:</b> {call[1]}\n"
			                              f"<b>Сумма:</b> {call[8]}$",
			                              reply_markup=em.receipt_button, parse_mode="HTML")
		else:
			await callback.message.answer(f"<b>Название задачи:</b> {call[0]}\n"
			                              f"<b>Описание:</b> {call[1]}\n"
			                              f"<b>Сумма:</b> {call[8]}$\n"
			                              f"<b>Описание:</b> {call[9]}",
			                              reply_markup=em.receipt_button, parse_mode="HTML")
	

async def callback_finish_tasks(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	if callback.data == "send_receipt":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		cursor.execute("UPDATE tasks SET status = ? WHERE short_name = ?", ["Выполнено ✅", call[0]])
		conn.commit()
		status = cursor.execute("SELECT status FROM tasks WHERE short_name = ?", [call[0]]).fetchone()[0]
		if call[9] is None:
			await bot.send_message(call[5], f"🔔 Ваша задача завершена!\n\n"
			                                f"<b>Название задачи:</b> {call[0]}\n"
			                                f"<b>Описание:</b> {call[1]}\n"
			                                f"<b>Статус:</b> {status}\n"
			                                f"<b>Исполнитель:</b> {call[7]}\n"
			                                f"<b>Сумма:</b> {call[8]}$", parse_mode="HTML")
		else:
			await bot.send_message(call[5], f"🔔 Ваша задача завершена!\n\n"
			                                f"<b>Название задачи:</b> {call[0]}\n"
			                                f"<b>Описание:</b> {call[1]}\n"
			                                f"<b>Статус:</b> {status}\n"
			                                f"<b>Исполнитель:</b> {call[7]}\n"
			                                f"<b>Сумма:</b> {call[8]}$\n"
			                                f"<b>Описание:</b> {call[9]}", parse_mode="HTML")
		await callback.message.answer('Чек был отправлен клиенту')

	if callback.data == "edit_receipt":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		if call[9] is None:
			await callback.message.answer(f"<b>Название задачи:</b> {call[0]}\n"
			                              f"<b>Описание:</b> {call[1]}\n"
			                              f"<b>Сумма:</b> {call[8]}$",
			                              reply_markup=em.edit_receipt, parse_mode="HTML")
		else:
			await callback.message.answer(f"<b>Название задачи:</b> {call[0]}\n"
			                              f"<b>Описание:</b> {call[1]}\n"
			                              f"<b>Сумма:</b> {call[8]}$\n"
			                              f"<b>Описание:</b> {call[9]}",
			                              reply_markup=em.edit_receipt, parse_mode="HTML")


async def callback_status_timer(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()

	if callback.data == "timer_start":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		global timer_start, start_time
		timer_start = True
		start_time = str(datetime.datetime.now())
		await callback.message.answer(
			f"<b>Краткое название:</b> {call[0]}\n<b>Сколько часов потрачено:</b> {call[6]}",
			reply_markup=em.timer_stop, parse_mode='HTML')

	if callback.data == "timer_stop":
		timer_start = False
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		date1 = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
		date2 = datetime.datetime.now()
		delta = date2 - date1
		count_hour = round(delta.total_seconds() / (60 * 60))
		check_how_hour = cursor.execute("SELECT timer FROM tasks WHERE short_name = ?", [call[0]]).fetchone()[0]
		if not check_how_hour > 0:
			cursor.execute("UPDATE tasks SET timer = ? WHERE short_name = ?", [count_hour, call[0]])
			conn.commit()
			result = cursor.execute(f'SELECT timer FROM tasks WHERE short_name = ?', [call[0]]).fetchone()[0]
			stake = cursor.execute(f'SELECT stake FROM users WHERE tg_id = {callback.from_user.id}').fetchone()[0]
			price = stake * count_hour
			cursor.execute(f"UPDATE tasks SET final_price = ? WHERE short_name = ?", [price, call[0]])
			conn.commit()
			await callback.message.answer(
				f"<b>Краткое название:</b> {call[0]}\n<b>Сколько часов потрачено:</b> {result}",
				reply_markup=em.timer_start, parse_mode='HTML')
		else:
			count_hour = round(delta.total_seconds() / (60 * 60)) + check_how_hour
			cursor.execute("UPDATE tasks SET timer = ? WHERE short_name = ?", [count_hour, call[0]])
			conn.commit()
			result = cursor.execute(f'SELECT timer FROM tasks WHERE short_name = ?', [call[0]]).fetchone()[0]
			stake = cursor.execute(f'SELECT stake FROM users WHERE tg_id = {callback.from_user.id}').fetchone()[0]
			price = stake * count_hour
			cursor.execute(f"UPDATE tasks SET final_price = ? WHERE short_name = ?", [price, call[0]])
			conn.commit()
			await callback.message.answer(
				f"<b>Краткое название:</b> {call[0]}\n<b>Сколько часов потрачено:</b> {result}",
				reply_markup=em.timer_start, parse_mode='HTML')


async def callback_edit_status(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()

	if callback.data == "status_read":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Прочитано 👀', call[0]])
		conn.commit()
		status_read = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [call[0]]).fetchone()[0]
		await callback.message.answer(
			f"<b>Краткое название:</b> {call[0]}\n<b>Описание:</b> {call[1]}\n<b>Дедлайн:</b> {call[2]}\n<b>Статус:</b> {status_read}\n<b>Клиент:</b> @{call[4]}({call[5]})",
			reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "status_start":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Начал выполнение ✏️', call[0]])
		conn.commit()
		status_start = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [call[0]]).fetchone()[0]
		await callback.message.answer(
			f"<b>Краткое название:</b> {call[0]}\n<b>Описание:</b> {call[1]}\n<b>Дедлайн:</b> {call[2]}\n<b>Статус:</b> {status_start}\n<b>Клиент:</b> @{call[4]}({call[5]})",
			reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "status_success":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Выполнено ✅', call[0]])
		conn.commit()
		status_success = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [call[0]]).fetchone()[0]
		await callback.message.answer(
			f"<b>Краткое название:</b> {call[0]}\n<b>Описание:</b> {call[1]}\n<b>Дедлайн:</b> {call[2]}\n<b>Статус:</b> {status_success}\n<b>Клиент:</b> @{call[4]}({call[5]})",
			reply_markup=em.edit_status, parse_mode='HTML')

	if callback.data == "status_canceled":
		await callback.answer()
		await callback.message.delete()
		call = looking_data_in_table(call_active_tasks_executor)
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Отменено ⛔️', call[0]])
		conn.commit()
		chat_id = cursor.execute("SELECT client_id FROM tasks WHERE short_name = ?", [call[0]]).fetchone()[0]
		await callback.message.answer(f"Задача <b>{call[0]}</b> была отклонена", parse_mode='HTML')
		await bot.send_message(chat_id, f"Выша задача с названием <b>\"{call[0]}\"</b> была отменена исполнителем <b>{call[7]}</b>. "
		                                f"Измените название/описание/дедлайн и попробуйте создать задачу еще раз.", parse_mode="HTML")
		cursor.execute("DELETE FROM tasks WHERE short_name = ?", [call[0]])
		conn.commit()


async def callback_notice_edit_status(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	if callback.data == "status_read_notice":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Прочитано 👀', name])
		conn.commit()
		status_read = cursor.execute("SELECT status FROM tasks WHERE short_name = ? ", [name]).fetchone()[0]
		await callback.message.answer(f"Задаче <b>{name}</b> был изменен статус на <b>{status_read}</b>.\n\nДля дальнейшего изменения статуса нажмите на кнопку <b>\"📚 Список задач 📚\"</b>", parse_mode='HTML')

	if callback.data == "status_canceled_notice":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {func.notice_id_task}').fetchone()[0]
		cursor.execute(f'UPDATE tasks SET status = ? WHERE short_name = ?', ['Отменено ⛔️', name])
		conn.commit()
		chat_id = cursor.execute("SELECT client_id FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
		executor_name = cursor.execute("SELECT executor FROM tasks WHERE short_name = ?", [name]).fetchone()[0]
		await callback.message.answer(f"Задача <b>{name}</b> была отклонена", parse_mode='HTML')
		await bot.send_message(chat_id, f"Выша задача с названием <b>\"{name}\"</b> была отменена исполнителем <b>{executor_name}</b>. "
		                                f"Измените название/описание/дедлайн и попробуйте создать задачу еще раз.", parse_mode="HTML")
		cursor.execute("DELETE FROM tasks WHERE short_name = ?", [name])
		conn.commit()


async def callback_edit_receipt(callback: types.CallbackQuery):
	# conn = sqlite3.connect('base.db')
	# cursor = conn.cursor()
	if callback.data == "add_description":
		await callback.answer()
		await callback.message.delete()
		await func.FSMAddDescriptionForReceipt.description_receipt.set()
		await callback.message.answer("Введите описание\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")

	if callback.data == "edit_final_price":
		await callback.answer()
		await callback.message.delete()
		await func.FSMEditFinalPrice.final_price.set()
		await callback.message.answer("Введите новую сумму\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")


def register_handler_executors(dp: Dispatcher):
	dp.register_message_handler(handler_executors, commands=["admin"])
	dp.register_message_handler(profile, text=["👤 Профиль 👤"])
	dp.register_message_handler(list_task, text=["📚 Список задач 📚"])
	dp.register_callback_query_handler(callback_handler_executors, text=["edit_profile_executor", "view_completed_tasks",
	                                                                     "rename_executor", "set_stake"])
	dp.register_callback_query_handler(callback_check_active_tasks_for_executor,
	                                   Text(startswith='active-tasks_'))
	dp.register_callback_query_handler(callback_select_task_executor, text=["edit_status", "start_execution",
	                                                                        "finish_task"])
	dp.register_callback_query_handler(callback_finish_tasks, text=["send_receipt", "edit_receipt"])
	dp.register_callback_query_handler(callback_status_timer, text=["timer_start", "timer_stop"])
	dp.register_callback_query_handler(callback_edit_status, text=["status_read", "status_start",
	                                                               "status_success", "status_canceled"])
	dp.register_callback_query_handler(callback_notice_edit_status, text=["status_read_notice", "status_canceled_notice"])
	dp.register_callback_query_handler(callback_edit_receipt, text=["add_description", "edit_final_price"])
