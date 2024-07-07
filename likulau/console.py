import os
import logging
from typing import Annotated, Union

import typer
import uvicorn

logger = logging.getLogger("likulau.console")
app = typer.Typer()


@app.command()
def run(
    host: Annotated[
        str,
        typer.Option(help="The host to serve on."),
    ] = "127.0.0.1",
    port: Annotated[
        Union[int, None],
        typer.Option(help="The port to serve on."),
    ] = None,
    reload: Annotated[
        bool,
        typer.Option(help="Enable auto-reload of the server when files change."),
    ] = False,
    root_path: Annotated[
        str,
        typer.Option(
            help="Tell your app that it is being served to the outside world with some path prefix set up in some termination proxy or similar."
        ),
    ] = "",
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
    workers: Annotated[
        Union[int, None],
        typer.Option(
            help="Use multiple worker processes. Cannot be used with --reload flag."
        ),
    ] = None,
):
    if not port:
        port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "likulau.app:create_app",
        host=host,
        port=port,
        log_level="info",
        reload=reload,
        root_path=root_path,
        proxy_headers=proxy_headers,
        factory=True,
        lifespan="on",
        workers=workers,
    )


@app.command()
def dev(
    host: Annotated[
        str,
        typer.Option(help="The host to serve on."),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(help="The port to serve on."),
    ] = 8000,
    root_path: Annotated[
        str,
        typer.Option(
            help="Tell your app that it is being served to the outside world with some path prefix set up in some termination proxy or similar."
        ),
    ] = "",
    proxy_headers: Annotated[
        bool,
        typer.Option(
            help="Enable/Disable X-Forwarded-Proto, X-Forwarded-For, X-Forwarded-Port to populate remote address info."
        ),
    ] = True,
):
    uvicorn.run(
        "likulau.app:create_app",
        host=host,
        port=port,
        log_level="info",
        root_path=root_path,
        proxy_headers=proxy_headers,
        factory=True,
        lifespan="on",
        reload=True,
    )


@app.command()
def build():
    raise NotImplementedError()


if __name__ == "__main__":
    app()
