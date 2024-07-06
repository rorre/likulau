import warnings

from starlette.config import Config

with warnings.catch_warnings(action="ignore"):
    env = Config(".env")
