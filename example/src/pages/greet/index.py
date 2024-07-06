import liku as e

from likulau.env import env


def page(props) -> e.HTMLElement:
    return e.p(children=f"Hello {env('NAME')}!")
