import logging

import typer
import uvicorn

from likulau.app import create_app

logger = logging.getLogger("likulau.console")
app = typer.Typer()


@app.command()
def run():
    logger.info("Initialize app")
    app = create_app()

    uvicorn.run(app, port=3000, log_level="info")


@app.command()
def build():
    print("TODO")


if __name__ == "__main__":
    app()
