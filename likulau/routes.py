from likulau.types import PageFunction


def methods(methods: list[str]):
    def inner(func: PageFunction):
        func._methods = methods
        return func

    return inner
