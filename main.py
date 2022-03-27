import os
from multiprocessing import Process

from bot import bot
from web import app

Process(target=lambda: app.run("0.0.0.0")).start()
bot.run(os.environ["TOKEN"])
