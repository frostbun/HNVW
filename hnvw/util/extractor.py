from youtube_dl import YoutubeDL

from ..model import Song
from .decorator import run_in_executor
from .validator import check_url

YDL_OPTIONS = {"format": "bestaudio"}
YDL_OPTIONS_NO_PLAYLIST = {**YDL_OPTIONS, "noplaylist": True}

@run_in_executor
def extract_one(url: str) -> Song:
    with YoutubeDL(YDL_OPTIONS_NO_PLAYLIST) as ydl:
        return Song.from_ydl(ydl.extract_info(url, False))


@run_in_executor
def extract_all(url: str) -> tuple[Song, list[Song]]:
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


@run_in_executor
def youtube_search(name: str, amount: int = 5) -> list[Song]:
    with YoutubeDL(YDL_OPTIONS) as ydl:
        return [ Song.from_ydl(entry) for entry in ydl.extract_info(f"ytsearch{amount}:{name}", False)["entries"] ]


async def extract_all_or_search(url: str) -> tuple[Song, list[Song]]:
    # input name
    if not await check_url(url):
        songs = await youtube_search(url, 1)
        return songs[0], songs
    # input url
    return await extract_all(url)
