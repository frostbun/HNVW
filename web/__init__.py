from flask import Flask, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("https://discord.com/api/oauth2/authorize?client_id=917296694247436298&permissions=8&scope=bot%20applications.commands")
