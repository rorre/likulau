from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass
import importlib
import inspect
from pathlib import Path

from liku.context import Context
from likulau.types import ProviderFunction
from likulau.utils import run_async


@dataclass
class Provider:
    ctx: Context
    provider: ProviderFunction
    dependencies: list[Context]


app_providers: dict[Context, Provider] = {}
resolve_queue: list[Context] = []


def setup_providers():
    global app_providers, resolve_queue

    providers: dict[Context, Provider] = {}
    for page in Path("src/providers").glob("**/*.py"):
        page = page.with_suffix("")
        module = ".".join(page.parts)

        page_mod = importlib.import_module(module)
        provider_obj = None
        for _, obj in inspect.getmembers(page_mod):
            if hasattr(obj, "_ctx"):
                provider_obj = obj

        if not provider_obj:
            raise Exception(f"Cannot find provider in {page_mod.__name__}. Have you decorated the function?")

        provider = Provider(
            provider_obj._ctx,
            provider_obj,
            provider_obj._deps,
        )
        providers[provider.ctx] = provider

    if not providers:
        return

    queue: list[Context] = []
    for provider in providers.values():
        for ctx_deps in provider.dependencies:
            if ctx_deps not in queue:
                queue.append(ctx_deps)

        queue.append(provider.ctx)

    app_providers = providers
    resolve_queue = queue


@asynccontextmanager
async def provide_all():
    async with AsyncExitStack() as stack:
        for ctx in resolve_queue:
            ctx_manager = await run_async(app_providers[ctx].provider)
            if hasattr(ctx_manager, "__aenter__"):
                await stack.enter_async_context(ctx_manager)  # type: ignore
            else:
                stack.enter_context(ctx_manager)  # type: ignore

        yield


def provider(ctx: Context, deps: list[Context]):
    def inner(func: ProviderFunction):
        func._ctx = ctx
        func._deps = deps
        return func

    return inner
