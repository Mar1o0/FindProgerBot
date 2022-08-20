from aiogram import types, Dispatcher
from keyboards import client_menu


async def command_start(message: types.Message):
	await message.answer("Здравствуйте!", reply_markup=client_menu.client_menu_kb)


async def add_task(message: types.Message):
	await message.answer("Для начала нужно выбрать исполнителя", reply_markup=client_menu.client_add_task_inb)


async def check_tasks(message: types.Message):
	await message.answer("Список активных задач", reply_markup=client_menu.client_check_tasks_inb)


async def callback_handler_client(callback: types.CallbackQuery):
	if callback.data == "select_executor":
		await callback.message.delete()
		await callback.message.answer("Была нажата кнопка \"Выбрать исполнителя\"")
		await callback.answer()

	if callback.data == "list_active_tasks":
		await callback.message.delete()
		await callback.message.answer("Была нажата кнопка \"Список активных задач\"")
		await callback.answer()


def register_handler_client(dp: Dispatcher):
	dp.register_message_handler(command_start, commands=["start"])
	dp.register_message_handler(add_task, text=["Добавить задачу"])
	dp.register_message_handler(check_tasks, text=["Проверить задачи"])
	dp.register_callback_query_handler(callback_handler_client, text=["select_executor",
	                                                                  "list_active_tasks"])

