from aiogram import types, Dispatcher
from create_bot import bot
from keyboards import client_menu


# @dp.message_handler(commands="start")
async def command_start(message: types.Message):
	await bot.send_message(message.from_user.id, "Здравствуйте!", reply_markup=client_menu.client_menu_kb)


def register_handler_client(dp: Dispatcher):
	dp.register_message_handler(command_start, commands=["start"])

