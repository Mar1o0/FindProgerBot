from aiogram.dispatcher import Dispatcher
from aiogram import Bot
import os

bot = Bot(token=os.getenv("TOKEN"))
dp = Dispatcher(bot)
