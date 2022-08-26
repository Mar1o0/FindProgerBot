from aiogram.utils import executor
from aiogram.utils.exceptions import BotBlocked
from aiogram import types
from create_bot import dp, bot
from handlers import client, executors, functions
import sqlite3


async def on_startup(_):
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
			final_price integer DEFAULT 0,
			description_receipt text DEFAULT Null
			)
			"""
	cursor.executescript(tables)
	user = cursor.execute(f'SELECT * FROM users').fetchall()
	print("[INFO] Бот в сети!")
	for chat_id in user:
		try:
			await bot.send_message(chat_id[1], "🔔 Бот снова работает!")
		except:
			pass


@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	print(f"[INFO] Меня заблокировал пользователь {update.message.from_user.username}!\n\tСообщение: {update.message.text}\n\tОшибка: {exception}")
	cursor.execute(f"DELETE FROM users WHERE tg_id = {update.message.from_user.id}")
	conn.commit()
	return True


client.register_handler_client(dp)
executors.register_handler_executors(dp)
functions.register_handler_function(dp)

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
