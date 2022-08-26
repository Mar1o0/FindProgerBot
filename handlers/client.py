from aiogram import types, Dispatcher
from keyboards import client_menu
from handlers import functions as func
from aiogram.dispatcher.filters import Text
import sqlite3

call_add_task = None
call_check_task = None


async def command_start(message: types.Message):
	func.first_join(message.from_user.id, message.from_user.first_name, message.from_user.username)
	await message.answer("Здравствуйте!", reply_markup=client_menu.client_menu_kb)


async def add_task(message: types.Message):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	data_executor = cursor.execute(f'SELECT * FROM users WHERE access_id = 10').fetchall()
	await message.answer("Для начала нужно выбрать исполнителя", reply_markup=func.add_task(data_executor))


async def callback_add_task(callback: types.CallbackQuery):
	global call_add_task
	call_add_task = int(callback.data.split("_")[1])
	await callback.answer()
	await callback.message.delete()
	await func.FSMAddTaskForExecutor.short_name.set()
	await callback.message.answer("Напишите краткое название\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")


async def check_tasks(message: types.Message):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	data_tasks = cursor.execute('SELECT * FROM tasks WHERE client_id = ? AND status != "Выполнено ✅"', [message.from_user.id]).fetchall()
	await message.answer("Список активных задач", reply_markup=func.check_tasks(data_tasks))


async def callback_check_tasks(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	global call_check_task
	call_check_task = int(callback.data.split("_")[1])
	await callback.answer()
	await callback.message.delete()
	short_name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_check_task}').fetchone()[0]
	description = cursor.execute(f'SELECT description FROM tasks WHERE id = {call_check_task}').fetchone()[0]
	deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {call_check_task}').fetchone()[0]
	status = cursor.execute(f'SELECT status FROM tasks WHERE id = {call_check_task}').fetchone()[0]
	executor = cursor.execute(f'SELECT executor FROM tasks WHERE id = {call_check_task}').fetchone()[0]
	await callback.message.answer(
		f"<b>Краткое название:</b> {short_name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status}\n<b>Исполнитель:</b> {executor}",
		reply_markup=client_menu.info_about_task, parse_mode='HTML')


async def callback_edit_task(callback: types.CallbackQuery):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()

	if callback.data == "edit_short_name":
		await callback.answer()
		await callback.message.delete()
		await func.FSMEditShortName.edit_short_name.set()
		await callback.message.answer("Напишите краткое название\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")

	if callback.data == "edit_description":
		await callback.answer()
		await callback.message.delete()
		await func.FSMEditDescription.edit_description.set()
		await callback.message.answer("Напишите описание задачи\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")

	if callback.data == "edit_deadline":
		await callback.answer()
		await callback.message.delete()
		await func.FSMEditDeadline.edit_deadline.set()
		await callback.message.answer("Напишите дедлайн работы\n\nДля отмены напишите слово <b>\"отмена\"</b>", parse_mode="HTML")

	if callback.data == "delete_task":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_check_task}').fetchone()[0]
		await callback.message.answer(f'Вы действительно хотите удалить задачу с названием "{name}"?',
		                              reply_markup=client_menu.delete_task_inb)

	if callback.data == "yes":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_check_task}').fetchone()[0]
		cursor.execute(f"DELETE FROM tasks WHERE id = {call_check_task}")
		conn.commit()
		await callback.message.answer(f"Задача {name} была удалена.")

	if callback.data == "no":
		await callback.answer()
		await callback.message.delete()
		name = cursor.execute(f'SELECT short_name FROM tasks WHERE id = {call_check_task}').fetchone()[0]
		description = cursor.execute(f'SELECT description FROM tasks WHERE id = {call_check_task}').fetchone()[0]
		deadline = cursor.execute(f'SELECT deadline FROM tasks WHERE id = {call_check_task}').fetchone()[0]
		status = cursor.execute(f'SELECT status FROM tasks WHERE id = {call_check_task}').fetchone()[0]
		executor = cursor.execute(f'SELECT executor FROM tasks WHERE id = {call_check_task}').fetchone()[0]
		await callback.message.answer(
			f"<b>Краткое название:</b> {name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status}\n<b>Исполнитель:</b> {executor}",
			reply_markup=client_menu.info_about_task, parse_mode='HTML')


def register_handler_client(dp: Dispatcher):
	dp.register_message_handler(command_start, commands=["start"])
	dp.register_message_handler(add_task, text=["📝 Добавить задачу 📝"])
	dp.register_callback_query_handler(callback_add_task, Text(startswith='add-task_'), state=None)
	dp.register_message_handler(check_tasks, text=["👁 Список активных задач 👁"])
	dp.register_callback_query_handler(callback_check_tasks, Text(startswith='check-task_'))
	dp.register_callback_query_handler(callback_edit_task, text=["edit_short_name", "edit_description",
	                                                             "edit_deadline", "delete_task", "yes", "no"])
