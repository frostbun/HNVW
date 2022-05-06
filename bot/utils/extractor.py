from youtube_dl import YoutubeDL

from ..models import Song
from .validator import check_url

YDL_OPTIONS = {"format": "bestaudio"}
YDL_NO_PLAYLIST_OPTIONS = {"format": "bestaudio", "noplaylist": True}

def extract_one(url: str) -> Song:
    with YoutubeDL(YDL_NO_PLAYLIST_OPTIONS) as ydl:
        return Song.from_ydl(ydl.extract_info(url, False))

def extract_all(url: str):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        result = ydl.extract_info(url, False)
        # playlist
        if "entries" in result:
            return (
                Song(
                    title = result["title"],
                    duration = sum(int(entry["duration"]) for entry in result["entries"]),
                    thumbnail = result["entries"][0]["thumbnails"][-1]["url"],
                    initial_url = result["webpage_url"],
                ),
                [ Song.from_ydl(entry) for entry in result["entries"] ]
            )
        # single song
        return Song.from_ydl(result), [ Song.from_ydl(result) ]

def youtube_search(name: str, amount: int = 5):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        return [ Song.from_ydl(entry) for entry in ydl.extract_info(f"ytsearch{amount}:{name}", False)["entries"] ]

def extract_all_or_search(url: str):
    # input name
    if not check_url(url):
        songs = youtube_search(url, 1)
        return songs[0], songs
    # input url
    return extract_all(url)
