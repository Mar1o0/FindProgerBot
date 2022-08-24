from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked
from aiogram import types
from create_bot import dp
from handlers import client, executors, functions


async def on_startup(_):
	print("[INFO] Бот в сети!")


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
	print(f"[INFO] Меня заблокировал пользователь {update.message.from_user.username}!\n\tСообщение: {update.message.text}\n\tОшибка: {exception}")
	return True


client.register_handler_client(dp)
executors.register_handler_executors(dp)
functions.register_handler_function(dp)

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
