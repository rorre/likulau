import importlib
import inspect
import logging
import re
import sys
import typing
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

import liku
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import Route

from likulau.hooks import RequestContext
from likulau._internal.providers import provide_all
from likulau.types import LayoutFunction, PageFunction, SSRFunction, StaticPathsFunction
from likulau._internal.utils import run_async

sys.path.append(".")
logger = logging.getLogger("likulau.routes")


@dataclass
class LikulauRoute[PropsType]:
    path: str
    page_func: PageFunction[PropsType]
    static_paths_func: StaticPathsFunction | None = None
    ssr_props_func: SSRFunction[PropsType] | None = None
    layout_func: LayoutFunction | None = None
    methods: list[str] | None = None

    def create_router_func(self):
        route = Route(self.path, create_route(self), methods=self.methods)
        route._likulau_route_info = self # type: ignore (intended for app builder)
        return route


def _sort_route(route: LikulauRoute):
    has_parameter = bool(re.search(r"\{.*?\}", route.path))
    return (has_parameter, route.path)


def _process_page_module(page_mod: ModuleType):
    if not hasattr(page_mod, "page"):
        raise Exception(f"Missing page() function in {page_mod.__name__}")

    props_type = None
    ssr_props_func = None
    if hasattr(page_mod, "get_ssr_props"):
        ssr_props_func = page_mod.get_ssr_props
        props_type = typing.get_type_hints(ssr_props_func).get("return")
        if not props_type:
            raise Exception(
                f"Could not determine props type for module {page_mod.__name__}"
            )

    static_paths_func = None
    if hasattr(page_mod, "get_static_paths"):
        static_paths_func = page_mod.get_static_paths

    layout_func = None
    if hasattr(page_mod, "layout"):
        layout_func = page_mod.layout
        layout_props_type = typing.get_type_hints(layout_func).get("props")
        if layout_props_type != props_type:
            raise Exception(
                "Props type returned from get_ssr_props() does not match layout(). "
                f"({layout_props_type} != {props_type})",
            )

    page_func = page_mod.page
    types = typing.get_type_hints(page_func)
    # TODO: Is there any way for us to check the distribution better?
    if types.get("return") not in (
        liku.HTMLElement,
        Response,
        liku.HTMLElement | Response,
    ):
        raise Exception(
            f"{page_mod.__name__}.page() does not have correct return type."
            f"Expected HTMLElement | Response, got {types.get('return')}"
        )

    if types.get("props") != props_type:
        raise Exception(
            "Props type returned from get_ssr_props() does not match main(). "
            f"({types.get('props')} != {props_type})",
        )

    methods = None
    if hasattr(page_func, "_methods"):
        methods = page_func._methods

    return page_func, static_paths_func, ssr_props_func, layout_func, methods


def discover_pages():
    routes: list[LikulauRoute] = []
    for page in Path("src/pages").glob("**/*.py"):
        page = page.with_suffix("")
        module = ".".join(page.parts)
        logger.debug(f"Loading: {str(page)} (Module {module})")

        page_mod = importlib.import_module(module)
        page_func = _process_page_module(page_mod)

        page_path = "/".join(page.parts[2:]).replace("[", "{").replace("]", "}")
        if page.stem == "index":
            page_path = "/".join(page_path.split("/")[:-1])

        page_path = "/" + page_path
        routes.append(LikulauRoute(page_path, *page_func))
    routes.sort(key=_sort_route)
    return routes


def create_route(route: LikulauRoute):
    async def inner(request: Request):
        props = None
        if route.ssr_props_func:
            props = await run_async(route.ssr_props_func, request)

        with RequestContext.provide(request):
            async with provide_all():
                if len(inspect.signature(route.page_func).parameters) == 1:
                    response = await run_async(route.page_func, props)  # type: ignore
                else:
                    response = await run_async(route.page_func)  # type: ignore

                if isinstance(response, liku.HTMLElement):
                    if route.layout_func:
                        response = await run_async(route.layout_func, props, response)
                    response = HTMLResponse(str(response))

        return response

    return inner
