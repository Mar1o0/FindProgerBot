from aiogram import types, Dispatcher
from create_bot import bot


# @dp.message_handler(commands="start")
async def command_start(message: types.Message):
	await bot.send_message(message.from_user.id, "Здравствуйте!")


def register_handler_client(dp: Dispatcher):
	dp.register_message_handler(command_start, commands="start")

