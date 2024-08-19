import importlib
import typing
from pathlib import Path
from typing import Any

import liku
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response

from likulau.hooks import ExceptionContext, RequestContext
from likulau.types import ErrorHandlerFunction
from likulau._internal.utils import run_async


def discover_error_handlers():
    handlers: dict[str | int, Any] = {}
    for page in Path("src/errors").glob("**/*.py"):
        page = page.with_suffix("")
        module = ".".join(page.parts)

        page_mod = importlib.import_module(module)
        if not hasattr(page_mod, "handler"):
            raise Exception(
                f"Cannot find handler function for exception handler {page_mod.__name__}"
            )

        types = typing.get_type_hints(page_mod.handler)
        if types.get("return") not in (liku.HTMLElement, Response):
            raise Exception(
                f"{page_mod.__name__}.page() does not have correct return type."
                f"Expected HTMLElement | Response, got {types.get('return')}"
            )
        page_func = create_error_handler(page_mod.handler)

        handlers[int(page.stem)] = page_func
    return handlers


def create_error_handler(func: ErrorHandlerFunction):
    async def exception_handler(request: Request, exception: HTTPException):
        with RequestContext.provide(request), ExceptionContext.provide(exception):
            response = await run_async(func)
            if isinstance(response, liku.HTMLElement):
                return HTMLResponse(str(response), status_code=exception.status_code)

            response.status_code = exception.status_code
            return response

    return exception_handler
