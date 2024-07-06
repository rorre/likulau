import logging

import typer
import uvicorn

from likulau.app import create_app

logger = logging.getLogger("likulau.console")
app = typer.Typer()


@app.command()
def run():
    uvicorn.run(
        "likulau.app:create_app",
        port=3000,
        log_level="info",
        factory=True,
        lifespan="on",
    )


@app.command()
def dev():
    uvicorn.run(
        "likulau.app:create_app",
        port=3000,
        log_level="info",
        reload=True,
        factory=True,
        lifespan="on",
    )


@app.command()
def build():
    print("TODO")


if __name__ == "__main__":
    app()
