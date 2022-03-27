import os
from multiprocessing import Process

from bot import bot
from web import app

from logging import getLogger
getLogger("werkzeug").disabled = True

Process(target=lambda: app.run("0.0.0.0", 8080)).start()
bot.run(os.environ["TOKEN"])
