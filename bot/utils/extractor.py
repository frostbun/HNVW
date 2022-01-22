from youtube_dl import YoutubeDL

from .validator import check_url
from ..models import Song

from configs import YDL_OPTIONS, YDL_NO_PLAYLIST_OPTIONS

def extract_one(url):
    with YoutubeDL(YDL_NO_PLAYLIST_OPTIONS) as ydl:
        return Song.from_ytdl(ydl.extract_info(url, False))

def extract_all(url):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        result = ydl.extract_info(url, False)
        # playlist
        if "entries" in result:
            return (
                [ 
                    Song.from_ytdl(entry)
                    for entry in result["entries"]
                ], 
                Song(
                    title = result["title"],
                    duration = sum(int(entry["duration"]) for entry in result["entries"]),
                    thumbnail = result["entries"][0]["thumbnails"][-1]["url"],
                    initial_url = result["webpage_url"],
                )
            )
        # single song
        return [ Song.from_ytdl(result) ], Song.from_ytdl(result)

def youtube_search(name, amount=5):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        return [ Song.from_ytdl(song) for song in ydl.extract_info(f"ytsearch{amount}:{name}", False)["entries"] ]

def extract_all_or_search(url):
    # input name
    if not check_url(url):
        songs = youtube_search(url, 1)
        return songs, songs[0]
    # input url
    return extract_all(url)
