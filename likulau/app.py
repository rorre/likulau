import importlib
import logging
from pathlib import Path
from typing import cast

from starlette.applications import Starlette
from starlette.routing import Mount, BaseRoute
from starlette.staticfiles import StaticFiles

from likulau.env import env
from likulau._internal.errors import discover_error_handlers
from likulau._internal.providers import setup_providers
from likulau._internal.routes import discover_pages

logger = logging.getLogger("likulau.app")


def create_app():
    logger.info("Discovering pages")
    routes = discover_pages()

    logger.info("Discovering error handlers")
    exception_handlers = discover_error_handlers()

    setup_providers()

    lifespan = None
    if Path("src/app.py").exists():
        custom_app = importlib.import_module("src.app")
        if hasattr(custom_app, "lifespan"):
            lifespan = custom_app.lifespan

    app_routes: list[BaseRoute] = list(map(lambda x: x.create_router_func(), routes))
    if Path("static").exists() and Path("static").is_dir():
        app_routes.append(
            Mount("/static", app=StaticFiles(directory="static"), name="static")
        )

    app = Starlette(
        env("DEBUG", cast=bool, default=False),
        routes=app_routes,
        exception_handlers=exception_handlers,
        lifespan=lifespan,
    )

    if Path("src/app.py").exists():
        logger.info("Found custom app file, running")
        custom_app = importlib.import_module("src.app")
        app = custom_app.app(app)

        if not app:
            raise Exception(
                "App overriden with None. Please ensure that you return the app inside the app() function!"
            )

    return cast(Starlette, app)
