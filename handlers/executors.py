from aiogram import types, Dispatcher
import config
from keyboards import executors_menu


async def handler_executors(message: types.Message):
	if message.from_user.id == config.admin_id:
		await message.answer("Вы перешли в меню \"Исполнитель\"", reply_markup=executors_menu.executors_menu_kb)


async def profile(message: types.Message):
	await message.answer("Нажата кнопка \"Профиль\"", reply_markup=executors_menu.executors_profile_inb)


async def list_task(message: types.Message):
	await message.answer("Нажата кнопка \"Список задач\"", reply_markup=executors_menu.executors_list_task_inb)


async def callback_handler_executors(callback: types.CallbackQuery):
	if callback.data == "edit_profile_executor":
		await callback.message.delete()
		await callback.message.answer("Была нажата кнопка \"Редактировать\"")
		await callback.answer()

	if callback.data == "view_completed_tasks":
		await callback.message.delete()
		await callback.message.answer("Была нажата кнопка \"Посмотреть выполненные задачи\"")
		await callback.answer()


def register_handler_executors(dp: Dispatcher):
	dp.register_message_handler(handler_executors, commands=["admin"])
	dp.register_message_handler(profile, text=["Профиль"])
	dp.register_message_handler(list_task, text=["Список задач"])
	dp.register_callback_query_handler(callback_handler_executors, text=["edit_profile_executor",
	                                                                     "view_completed_tasks"])
