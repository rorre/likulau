import typing as t
from collections.abc import Awaitable

import liku
from starlette.datastructures import FormData
from starlette.requests import Request
from starlette.responses import Response

type MaybeAwaitable[T] = T | Awaitable[T]
type PageReturn = liku.HTMLElement | Response
type PageFunction[PropsType] = (
    t.Callable[[PropsType], MaybeAwaitable[PageReturn]]
    | t.Callable[[], MaybeAwaitable[PageReturn]]
)
type RPCFunction = t.Callable[[FormData], MaybeAwaitable[PageReturn]]
type SSRFunction[PropsType] = t.Callable[[Request], MaybeAwaitable[PropsType]]
type StaticPathsFunction = t.Callable[[], MaybeAwaitable[list[dict[str, t.Any]]]]
type ErrorHandlerFunction = t.Callable[[], MaybeAwaitable[PageReturn]]
type LayoutFunction[PropsType] = t.Callable[
    [PropsType, liku.HTMLElement], MaybeAwaitable[PageReturn]
]
type ProviderFunction = t.Callable[
    [], MaybeAwaitable[t.ContextManager | t.AsyncContextManager]
]
