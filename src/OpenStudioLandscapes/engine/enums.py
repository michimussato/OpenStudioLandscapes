__all__ = [
    "ComposeScope",
    "ComposeNetworkMode",
    "DockerRepositoryType",
    "DockerConfig",
]


import enum
import os

# Todo
#  - maybe use env var for secret
try:
    from __SECRET__.secrets import secrets as _secrets
except ModuleNotFoundError:
    # context.log.exception("Failed to import secrets from __SECRET__.secrets")
    _secrets: dict = {}


class ComposeScope(enum.StrEnum):
    DEFAULT = "default"
    WORKER = "worker"
    HARBOR = "harbor"


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


class DockerRegistry(enum.StrEnum):
    DOCKER = "docker.io"
    GIT_HUB = "ghcr.io"
    GOOGLE = "gcr.io"
    LOCAL_LOCALHOST = "localhost"
    LOCAL_HARBOR = "harbor.farm.evil"
    LOCAL_MINIBOSS = os.environ.get("IP_MASTER", "localhost")
    LOCAL_192_168_1_162 = "192.168.1.162"
    LOCAL_192_168_1_163 = "192.168.1.163"
    LOCAL_192_168_1_164 = "192.168.1.164"
    LOCAL_192_168_1_165 = "192.168.1.165"
    # HARBOR = ""  # https://goharbor.io/


class RegistryCredentials(enum.Enum):
    DOCKER_HUB_LOGIN1 = {
        "registry_type": DockerRegistry.DOCKER,
        "registry_username": _secrets.get("SECRET_DOCKER_DOCKERHUB_USERNAME"),
        "registry_password": _secrets.get("SECRET_DOCKER_DOCKERHUB_PASSWORD"),
    }
    # Example:
    GIT_HUB_LOGIN1 = {
        "registry_type": DockerRegistry.GIT_HUB,
        "registry_username": _secrets.get(""),
        "registry_password": _secrets.get(""),
    }


class DockerRepositoryType(enum.StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class DockerConfig(enum.Enum):
    _REPOSITORY_NAME = "michimussato".lower()
    # Do not:
    # - repeat special characters multiple times (like "__")
    # - use capitals in repository names
    LOCAL_NO_PUSH = {
        "docker_push": False,
        "docker_use_local": True,
        "docker_registry_url": None,
        "docker_registry_port": None,
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
    DOCKER_HUB = {
        "docker_push": True,
        "docker_use_local": False,
        "docker_registry_url": "docker.io",
        "docker_registry_port": None,
        "docker_registry_username": _secrets.get("SECRET_DOCKER_DOCKERHUB_USERNAME"),
        "docker_registry_password": _secrets.get("SECRET_DOCKER_DOCKERHUB_PASSWORD"),
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC.value,
    }
    REGISTRY_LOCAL_192_168_1_163 = {
        "docker_push": True,
        "docker_use_local": True,
        "docker_registry_url": DockerRegistry.LOCAL_192_168_1_163.value,
        "docker_registry_port": "5000",
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
    LOCAL_LOCALHOST = {
        "docker_push": True,
        "docker_use_local": True,
        "docker_registry_url": DockerRegistry.LOCAL_LOCALHOST.value,
        "docker_registry_port": "443",
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
    LOCAL_HARBOR = {
        # https://github.com/goharbor/harbor
        # https://medium.com/@Shamimw/setting-up-harbor-docker-registry-installation-and-pushing-docker-images-a8b3db6fca6a
        "docker_push": True,
        "docker_use_local": False,
        "docker_registry_url": DockerRegistry.LOCAL_HARBOR.value,
        "docker_registry_port": "80",
        "docker_registry_username": "admin",
        "docker_registry_password": "Harbor12345",
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
    LOCAL_MINIBOSS = {
        "docker_push": True,
        "docker_use_local": True,
        "docker_registry_url": DockerRegistry.LOCAL_MINIBOSS.value,
        "docker_registry_port": "5000",
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC,
    }
