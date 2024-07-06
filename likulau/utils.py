from asyncio import iscoroutinefunction
from collections.abc import Awaitable
from typing import Callable

from asyncer import asyncify


async def run_async[**P, T](func: Callable[P, T | Awaitable[T]], *args: P.args, **kwargs: P.kwargs) -> T:
    if iscoroutinefunction(func):
        return await func(*args, **kwargs)

    return await asyncify(func)(*args, **kwargs)  # type: ignore
