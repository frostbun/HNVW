import os

from discord import Color

TOKEN = os.environ["TOKEN"]
COMMAND_PREFIX = "$"
EMBED_COLOR = Color.red()
VIEW_TIMEOUT = None

DATABASE = "db.sqlite3"

YDL_OPTIONS = {"format": "bestaudio"}
YDL_NO_PLAYLIST_OPTIONS = {"format": "bestaudio", "noplaylist": True}

FFMPEG_OPTIONS = {"bitrate": 128, "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", "options": "-vn"}
