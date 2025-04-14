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
except ModuleNotFoundError as e:
    # context.log.exception("Failed to import secrets from __SECRET__.secrets")
    print(f"ModuleNotFoundError captured: {e}")
    _secrets: dict = {}
except SyntaxError as e:
    print(f"SyntaxError captured: {e}")
    # SyntaxError can happen when nox testing from within a different module.
    # OpenStudioLandscapes is cloned to local tmp directory while the local clone
    # is *of course* not git-crypt unlock'ed.
    _secrets: dict = {}


class ComposeScope(enum.StrEnum):
    DEFAULT = "default"
    WORKER = "worker"
    LICENSE_SERVER = "license_server"


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
    LOCAL_LOCALHOST = "localhost"
    LOCAL_HARBOR = "harbor.farm.evil"
    LOCAL_MINIBOSS = os.environ.get("IP_MASTER", "localhost")


# class RegistryCredentials(enum.Enum):
#     # Example:
#     # GIT_HUB_LOGIN1 = {
#     #     "registry_type": DockerRegistry.GIT_HUB,
#     #     "registry_username": _secrets.get(""),
#     #     "registry_password": _secrets.get(""),
#     # }
#     pass


class DockerRepositoryType(enum.StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class DockerConfig(enum.Enum):
    _REPOSITORY_NAME = "openstudiolandscapes".lower()
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
        "docker_repository_type": DockerRepositoryType.PUBLIC.value,
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
    LOCAL_LOCALHOST = {
        "docker_push": True,
        "docker_use_local": True,
        "docker_registry_url": DockerRegistry.LOCAL_LOCALHOST.value,
        "docker_registry_port": "443",
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC.value,
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
        "docker_repository_type": DockerRepositoryType.PUBLIC.value,
    }
    LOCAL_MINIBOSS = {
        "docker_push": True,
        "docker_use_local": True,
        "docker_registry_url": DockerRegistry.LOCAL_MINIBOSS.value,
        "docker_registry_port": "5000",
        "docker_registry_username": None,
        "docker_registry_password": None,
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PUBLIC.value,
    }
