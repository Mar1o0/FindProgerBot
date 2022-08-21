import sqlite3
import datetime


def first_join(tg_id, name, login, access_id):
	conn = sqlite3.connect('base.db')
	cursor = conn.cursor()
	conn.execute("CREATE TABLE IF NOT EXISTS users(tg_id, name, login, access_id, date_reg)")

	row = cursor.execute(f'SELECT * FROM users WHERE tg_id = "{tg_id}"').fetchall()

	if len(row) == 0:
		cursor.execute(f'INSERT INTO users VALUES ("{tg_id}", "{name}", "{login}", "{access_id}", "{datetime.datetime.now()}")')
		conn.commit()
