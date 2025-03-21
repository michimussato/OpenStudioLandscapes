__all__ = [
    # "ComposeScope",
    "ComposeNetworkMode",
    "DockerRepositoryType",
    "DockerConfig",
]


import enum


# Todo
#  - maybe use env var for secret
try:
    from __SECRET__.secrets import secrets as _secrets
except ModuleNotFoundError:
    # context.log.exception("Failed to import secrets from __SECRET__.secrets")
    _secrets: dict = {}


# Todo:
# class ComposeScope(enum.StrEnum):
#     DEFAULT = "default"
#     WORKER = "worker"


class ComposeNetworkMode(enum.StrEnum):
    # https://docs.docker.com/engine/network/
    # Docker Compose Ports settings
    # will be ignored if other than "default"
    DEFAULT = "default"
    BRIDGE = "bridge"
    HOST = "host"
    NONE = "none"
    OVERLAY = "overlay"
    IPVLAN = "ipvlan"
    MACVLAN = "macvlan"


class DockerRepositoryType(enum.StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class DockerConfig(enum.Enum):
    _REPOSITORY_NAME = "michimussato".lower()
    # Do not:
    # - repeat special characters multiple times (like "__")
    # - use capitals in repository names
    DOCKER_HUB = {
        "docker_use_local": False,
        "docker_registry_url": "docker.io",
        "docker_registry_port": None,
        "docker_registry_username": _secrets.get("SECRET_DOCKER_DOCKERHUB_USERNAME"),
        "docker_registry_password": _secrets.get("SECRET_DOCKER_DOCKERHUB_PASSWORD"),
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
    REGISTRY_LOCAL = {
        "docker_use_local": False,
        "docker_registry_url": "localhost",
        "docker_registry_port": "5000",
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
    LOCAL = {
        "docker_use_local": True,
        "docker_registry_url": None,
        "docker_registry_port": None,
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
