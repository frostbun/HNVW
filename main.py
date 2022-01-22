from threading import Thread

from bot import bot
from web import app

from configs import TOKEN

Thread(target=lambda: app.run("0.0.0.0", 8080)).start()
bot.run(TOKEN)
