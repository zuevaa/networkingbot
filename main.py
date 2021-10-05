from app.Bot import Bot
from db.DbHelper import DbHelper
from app.Scheduler import Scheduler

dbHelper = DbHelper()
bot = Bot(dbHelper)
scheduler = Scheduler(bot, dbHelper)
