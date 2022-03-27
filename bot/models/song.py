from dataclasses import dataclass

from ..components import Embed
from ..utils.formatter import format_duration

@dataclass
class Song:
    title: str
    duration: str
    thumbnail: str
    initial_url: str
    play_url: str = None

    def __post_init__(self):
        self.duration = int(self.duration)

    def get_embed(self, title: str) -> Embed:
        return Embed(
            title = title,
            desc = f"**[{self.title}]({self.initial_url})**",
            footer_text = f"Duration: {format_duration(self.duration)}",
            thumbnail = self.thumbnail,
        )

    @classmethod
    def from_ydl(cls, song: dict):
        return cls(
            title = song["title"],
            duration = song["duration"],
            thumbnail = song["thumbnails"][-1]["url"],
            initial_url = song["webpage_url"],
            play_url = song["url"],
        )
