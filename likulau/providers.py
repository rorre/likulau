from liku.context import Context
from likulau.types import ProviderFunction


def provider(ctx: Context, deps: list[Context]):
    def inner(func: ProviderFunction):
        func._ctx = ctx
        func._deps = deps
        return func

    return inner
