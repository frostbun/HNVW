from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return  """ <script>
                location.href = 'https://discord.com/api/oauth2/authorize?client_id=917296694247436298&permissions=8&scope=bot%20applications.commands'
                </script>
            """

from logging import getLogger
getLogger("werkzeug").disabled = True
