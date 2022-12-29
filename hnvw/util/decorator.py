from asyncio import get_event_loop
from functools import wraps


def run_in_executor(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await get_event_loop().run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper
