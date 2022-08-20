from aiogram import types, Dispatcher
from create_bot import bot
import config
from keyboards import executors_menu


# @bot.message_handler(commands=['admin'])
async def handler_executors(message: types.Message):
	if message.from_user.id == config.admin_id:
		await bot.send_message(message.from_user.id, "Вы перешли в меню \"Исполнитель\"", reply_markup=executors_menu.executors_menu_kb)
	else:
		await bot.send_message(message.from_user.id, "Ты не админ! Но глянь какая клава у админа)", reply_markup=executors_menu.executors_menu_kb)


def register_handler_executors(dp: Dispatcher):
	dp.register_message_handler(handler_executors, commands=["admin"])
