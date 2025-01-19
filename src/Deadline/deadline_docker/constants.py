import pathlib


__all__ = [
    "DOCKER_USE_CACHE",
    "MONGODB_INSIDE_CONTAINER",
    "DOT_DOCKER_ROOT",
]


DOCKER_USE_CACHE = False
MONGODB_INSIDE_CONTAINER = False
DOT_DOCKER_ROOT = pathlib.Path("~/git/repos/deadline-docker/.docker").expanduser()
