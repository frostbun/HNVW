from aiohttp import ClientSession


async def check_url(url: str) -> bool:
    try:
        async with ClientSession() as session:
            async with session.head(url) as response:
                return response.status < 400
    except Exception:
        return False
