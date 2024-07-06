import importlib
import logging
from pathlib import Path

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

    app = Starlette(
        env("DEBUG", cast=bool, default=False),
        routes=[
            *list(map(lambda x: x.create_router_func(), routes)),
            Mount("/static", app=StaticFiles(directory="static"), name="static"),
        ],
        exception_handlers=exception_handlers,
    )
    if Path("src/pages/_app.py").exists():
        logger.info("Found custom app file, running")
        custom_app = importlib.import_module("src.pages._app")
        app: Starlette = custom_app.app(app)

    return app
