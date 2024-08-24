from pathlib import Path
from starlette.testclient import TestClient
from starlette.routing import Route

from likulau._internal.console import console
from likulau._internal.routes import LikulauRoute
from likulau._internal.utils import run_async
from likulau.app import create_app


async def request_route(client: TestClient, route: Route, likulau_route: LikulauRoute):
    if not likulau_route.static_paths_func and len(route.param_convertors) != 0:
        console.print("    [yellow]Skipped because no get_static_paths() while having required arguments")
        return

    if likulau_route.static_paths_func:
        all_params = await run_async(likulau_route.static_paths_func)
    else:
        all_params = [{}]
    for params in all_params:
        urlpath = route.url_path_for(route.name, **params)
        yield (urlpath, client.get(urlpath))


async def build_app(target_directory: Path):
    app = create_app()
    client = TestClient(app)

    for route in app.routes:
        if not isinstance(route, Route):
            console.print("[yellow]Skipping non starlette Route paths")
            continue

        try:
            route_info: LikulauRoute | None = route._likulau_route_info  # type: ignore
            if not route_info:
                raise AttributeError()
        except AttributeError:
            console.print(f"[yellow]Cannot find route information for {route.path}, skipping.")
            continue

        console.print(f"[*] Building {route.path}")
        async for path, response in request_route(client, route, route_info):
            path = path.lstrip("/").rstrip("/")
            target_file = target_directory.joinpath(path).resolve()
            if not target_file.is_relative_to(target_directory):
                raise ValueError("Path is invalid")

            target_file = target_file / "index.html"
            target_file.parent.mkdir(parents=True, exist_ok=True)
            response.raise_for_status()

            assert not target_file.exists()
            with open(target_file, "wb") as fwrite:
                fwrite.write(response.content)

            console.print(f"    [green][*] Page {path} built to {target_file}")

    console.print("[green][*] Finished!")
