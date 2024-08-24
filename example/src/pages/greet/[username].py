from dataclasses import dataclass
import liku as e

from likulau.hooks import use_request

from starlette.requests import Request


@dataclass
class UsernameProps:
    info: str


def get_static_paths():
    return [
        {"username": "ren"},
        {"username": "example"},
        {"username": "epicgamer"},
    ]


def page(props: UsernameProps) -> e.HTMLElement:
    request = use_request()
    return e.p(children=f"Hello {request.path_params['username']}! ({props.info})")


def get_ssr_props(request: Request) -> UsernameProps:
    return UsernameProps("I'm from props!")
