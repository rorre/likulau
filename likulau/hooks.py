from liku.context import Context, use_context
from starlette.exceptions import HTTPException
from starlette.requests import Request

RequestContext = Context[Request]("request")
ExceptionContext = Context[HTTPException]("exception")


def use_request() -> Request:
    return use_context(RequestContext)


def use_exception() -> HTTPException:
    return use_context(ExceptionContext)
