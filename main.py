from aiogram.utils import executor
from create_bot import dp
from handlers import client, executors


async def on_startup(_):
	print("Бот в сети!")


client.register_handler_client(dp)
# executors.register_handler_executors(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

