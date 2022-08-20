from aiogram.utils import executor
from create_bot import dp
from handlers import client, executors


async def on_startup(_):
	print("[INFO] Бот в сети!")


client.register_handler_client(dp)
executors.register_handler_executors(dp)

executor.start_polling(dp, skip_updates=False, on_startup=on_startup)

