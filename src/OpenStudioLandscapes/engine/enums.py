__all__ = [
    "GroupIn",
    "OpenStudioLandscapesConfig",
    "ComposeScope",
    "ComposeNetworkMode",
    "DockerRepositoryType",
    "DockerConfig",
]

import enum


class GroupIn(enum.StrEnum):
    BASE_IN = "group_out_base"
    FEATURE_IN = "feature_out"


class OpenStudioLandscapesConfig(enum.StrEnum):
    DEFAULT = "default"
    PRODUCTION = "production"
    DEVELOPMENT = "development"


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
    LOCAL_LOCALHOST = "localhost"
    LOCAL_HARBOR = "harbor.farm.evil"
    # LOCAL_MINIBOSS = os.environ.get("IP_MASTER", "localhost")


class DockerRepositoryType(enum.StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


class DockerConfig(enum.Enum):
    _REPOSITORY_NAME = "openstudiolandscapes".lower()
    # Do not:
    # - repeat special characters multiple times (like "__")
    # - use capitals in repository names
    # Todo:
    #  - [ ] LOCAL_NO_PUSH is NOT SUPPORTED YET. Should it be?
    #  - [ ] Whether to use http or https
    # LOCAL_NO_PUSH = {
    #     "docker_push": False,
    #     "docker_use_local": True,
    #     "docker_registry_url": None,
    #     "docker_registry_port": None,
    #     "docker_registry_username": None,
    #     "docker_registry_password": None,
    #     "docker_repository": _REPOSITORY_NAME,
    #     "docker_repository_type": DockerRepositoryType.PUBLIC,
    # }
    LOCAL_HARBOR = {
        # https://github.com/goharbor/harbor
        # https://medium.com/@Shamimw/setting-up-harbor-docker-registry-installation-and-pushing-docker-images-a8b3db6fca6a
        # Todo
        #  - [ ] HTTP is deprecated
        "docker_push": True,
        "docker_use_local": False,
        "docker_registry_url": DockerRegistry.LOCAL_HARBOR,
        "docker_registry_port": "80",
        "docker_registry_username": "admin",
        "docker_registry_password": "Harbor12345",
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PRIVATE,
    }
