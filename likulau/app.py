import importlib
import logging
from pathlib import Path
from typing import cast

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

from likulau.env import env
from likulau.errors import discover_error_handlers
from likulau.routes import discover_pages

logger = logging.getLogger("likulau.app")


def create_app():
    logger.info("Discovering pages")
    routes = discover_pages()

    logger.info("Discovering error handlers")
    exception_handlers = discover_error_handlers()

    lifespan = None
    if Path("src/app.py").exists():
        custom_app = importlib.import_module("src.app")
        if hasattr(custom_app, "lifespan"):
            lifespan = custom_app.lifespan

    app = Starlette(
        env("DEBUG", cast=bool, default=False),
        routes=[
            *list(map(lambda x: x.create_router_func(), routes)),
            Mount("/static", app=StaticFiles(directory="static"), name="static"),
        ],
        exception_handlers=exception_handlers,
        lifespan=lifespan,
    )

    if Path("src/app.py").exists():
        logger.info("Found custom app file, running")
        custom_app = importlib.import_module("src.app")
        app = custom_app.app(app)

    return cast(Starlette, app)
