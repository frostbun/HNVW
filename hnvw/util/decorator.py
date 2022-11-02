from asyncio import get_event_loop
from functools import partial, wraps


def run_in_executor(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        pfunc = partial(func, *args, **kwargs)
        return await get_event_loop().run_in_executor(None, pfunc)
    return wrapper
