from ..components import Embed
from ..utils.formatter import format_duration

class Song:

    def __init__(self, title, duration, thumbnail, initial_url, play_url=None):
        self.title = title
        self.duration = int(duration)
        self.thumbnail = thumbnail
        self.initial_url = initial_url
        self.play_url = play_url

    def get_embed(self, title):
        return Embed(
            title = title,
            desc = f"**[{self.title}]({self.initial_url})**",
            footer = f"*Duration: {format_duration(self.duration)}*",
            thumbnail = self.thumbnail,
        )

    @staticmethod
    def from_ytdl(song):
        return Song(
            title=song["title"],
            duration=song["duration"],
            thumbnail=song["thumbnails"][-1]["url"],
            initial_url=song["webpage_url"],
            play_url=song["url"],
        )
