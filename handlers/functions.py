import sqlite3
import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from handlers import client
from create_bot import bot
from keyboards import executors_menu


notice_id_task = None


class FSMAddTaskForExecutor(StatesGroup):
	short_name = State()
	description = State()
	deadline = State()


class FSMEditShortName(StatesGroup):
	edit_short_name = State()


class FSMEditDescription(StatesGroup):
	edit_description = State()


class FSMEditDeadline(StatesGroup):
	edit_deadline = State()


class FSMEditNameInProfile(StatesGroup):
	new_name = State()


class FSMEditStakeExecutor(StatesGroup):
	new_stake = State()


def first_join(tg_id, name, login):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	tables = """
			CREATE TABLE IF NOT EXISTS users(
			id integer PRIMARY KEY, 
			tg_id integer NOT NULL, 
			name text, 
			login text NOT NULL, 
			access_id integer NOT NULL DEFAULT 2, 
			date_reg text NOT NULL, 
			stake integer DEFAULT 0
			);
			CREATE TABLE IF NOT EXISTS tasks(
			id integer PRIMARY KEY, 
			short_name text NOT NULL, 
			description text NOT NULL,
			deadline text NOT NULL, 
			client text NOT NULL, 
			client_id integer NOT NULL, 
			executor text NOT NULL, 
			executor_id integer NOT NULL, 
			status text DEFAULT "В обработке 🕔",
			timer integer DEFAULT 0,
			final_price real DEFAULT 0
			)
			"""
	cursor.executescript(tables)
	row = cursor.execute(f'SELECT * FROM users WHERE tg_id = "{tg_id}"').fetchall()

	if len(row) == 0:
		datatime = str(datetime.datetime.now())
		cursor.execute(f'INSERT INTO users(tg_id, name, login, date_reg) \
		VALUES ("{tg_id}", "{name}", "{login}", "{datatime[:19]}")')
		conn.commit()


def add_task(data_executor):
	client_add_task_inb = InlineKeyboardMarkup()
	for i in data_executor:
		client_add_task_inb.add(
			InlineKeyboardButton(f"{i[2]} | {i[6]}$/час", callback_data=f"add-task_{i[0]}")
		)
	return client_add_task_inb


async def cancel_input(message: types.Message, state: FSMContext):
	current_state = await state.get_state()
	if current_state is None:
		return
	await state.finish()
	await message.answer("Отменено")


async def add_task_short_name(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['short_name'] = message.text
	await FSMAddTaskForExecutor.next()
	await message.answer("Напишите описание самой задачи максимально подробно")


async def add_task_description(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['description'] = message.text
	await FSMAddTaskForExecutor.next()
	await message.answer("Напишите дедлайн работы")


async def add_task_deadline(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		data['deadline'] = message.text
		conn = sqlite3.connect('base.db')
		cursor = conn.cursor()
		short_name = data["short_name"]
		description = data["description"]
		deadline = data["deadline"]
		executor_name = cursor.execute(f'SELECT name FROM users WHERE id = {client.call_add_task}').fetchone()[0]
		executor_id = cursor.execute(f'SELECT tg_id FROM users WHERE id = {client.call_add_task}').fetchone()[0]
		cursor.execute(
			f"INSERT INTO tasks(short_name, description, deadline, client, client_id, executor, executor_id) VALUES('{short_name}', '{description}', '{deadline}', '{message.from_user.username}', '{message.from_user.id}', '{executor_name}', '{executor_id}')")
		conn.commit()
	await message.answer(
		f"Задача успешно добавлена. Ожидайте ответа от исполнителя.\nЗадачу можно посмотреть по кнопке <b>\"Проверить задачи\"</b>",
		parse_mode='HTML')
	status = cursor.execute(f"SELECT status FROM tasks WHERE short_name = ?", [short_name]).fetchone()[0]
	global notice_id_task
	notice_id_task = cursor.execute(f"SELECT id FROM tasks WHERE short_name = ?", [short_name]).fetchone()[0]
	await bot.send_message(
		cursor.execute(f"SELECT executor_id FROM tasks WHERE short_name = ?", [short_name]).fetchone()[0],
		f"<b>Пришла новая задача!</b>\n<b>Отправитель:</b> {message.from_user.username}({message.from_user.id})\n<b>Название:</b> {short_name}\n<b>Описание:</b> {description}\n<b>Дедлайн:</b> {deadline}\n<b>Статус:</b> {status}",
		parse_mode='HTML', reply_markup=executors_menu.notice_edit_status)
	await state.finish()


def check_tasks(data_tasks):
	list_tasks = InlineKeyboardMarkup()
	for i in data_tasks:
		list_tasks.add(
			InlineKeyboardButton(f"{i[1]}", callback_data=f"check-task_{i[0]}")
		)
	return list_tasks


async def edit_short_name(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		conn = sqlite3.connect('base.db')
		cursor = conn.cursor()
		data['short_name'] = message.text
		short_name = data["short_name"]
		id = client.call_check_task
		cursor.execute(f"UPDATE tasks SET short_name = ? WHERE id = ?", [short_name, id])
		conn.commit()
	await message.answer("Название изменено")
	await state.finish()


async def edit_description(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		conn = sqlite3.connect('base.db')
		cursor = conn.cursor()
		data['description'] = message.text
		description = data["description"]
		id = client.call_check_task
		cursor.execute(f"UPDATE tasks SET description = ? WHERE id = ?", [description, id])
		conn.commit()
	await message.answer("Описание изменено")
	await state.finish()


async def edit_deadline(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		conn = sqlite3.connect('base.db')
		cursor = conn.cursor()
		data['deadline'] = message.text
		deadline = data["deadline"]
		id = client.call_check_task
		cursor.execute(f"UPDATE tasks SET deadline = ? WHERE id = ?", [deadline, id])
		conn.commit()
	await message.answer("Дедлайн изменен")
	await state.finish()


async def edit_new_name(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		conn = sqlite3.connect('base.db')
		cursor = conn.cursor()
		data['new_name'] = message.text
		new_name = data["new_name"]
		cursor.execute(f"UPDATE users SET name = ? WHERE tg_id = ?", [new_name, message.from_user.id])
		conn.commit()
	await message.answer("Имя изменено")
	await state.finish()


async def edit_stake_executor(message: types.Message, state: FSMContext):
	async with state.proxy() as data:
		conn = sqlite3.connect('base.db')
		cursor = conn.cursor()
		try:
			data['new_stake'] = int(message.text)
			if data['new_stake'] <= 0:
				raise ValueError
			else:
				new_stake = data["new_stake"]
				cursor.execute(f"UPDATE users SET stake = ? WHERE tg_id = ?", [new_stake, message.from_user.id])
				conn.commit()
				await message.answer("Ставка сохранена")
				await state.finish()
		except TypeError:
			await FSMEditStakeExecutor.new_stake.set()
			await message.answer("Введите положительное целочисленное число!")
		except ValueError:
			await FSMEditStakeExecutor.new_stake.set()
			await message.answer("Введите положительное целочисленное число!")


def check_active_tasks_for_executor(data_tasks):
	list_active_tasks = InlineKeyboardMarkup()
	for i in data_tasks:
		list_active_tasks.add(
			InlineKeyboardButton(f"{i[1]}", callback_data=f"active-tasks_{i[0]}")
		)
	return list_active_tasks


def register_handler_function(dp: Dispatcher):
	dp.register_message_handler(cancel_input, Text(equals='отмена', ignore_case=True), state="*")
	dp.register_message_handler(add_task_short_name, state=FSMAddTaskForExecutor.short_name)
	dp.register_message_handler(add_task_description, state=FSMAddTaskForExecutor.description)
	dp.register_message_handler(add_task_deadline, state=FSMAddTaskForExecutor.deadline)
	dp.register_message_handler(edit_short_name, state=FSMEditShortName.edit_short_name)
	dp.register_message_handler(edit_description, state=FSMEditDescription.edit_description)
	dp.register_message_handler(edit_deadline, state=FSMEditDeadline.edit_deadline)
	dp.register_message_handler(edit_new_name, state=FSMEditNameInProfile.new_name)
	dp.register_message_handler(edit_stake_executor, state=FSMEditStakeExecutor.new_stake)
