import os

from flask import Flask, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(f"https://discord.com/api/oauth2/authorize?client_id={os.environ['BOT_ID']}&permissions=8&scope=bot%20applications.commands")
