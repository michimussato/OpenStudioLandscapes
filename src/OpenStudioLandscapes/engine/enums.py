__all__ = [
    "GroupIn",
    "OpenStudioLandscapesConfig",
    "FeatureVolumeType",
    "ComposeScope",
    "ComposeCmdExclusion",
    "ComposeNetworkMode",
    "DockerRepositoryType",
    "DockerConfig",
    "DefaultDicts",
]

import enum

from dagster import EnvVar


class GroupIn(enum.StrEnum):
    BASE_IN = "group_out_base"
    FEATURE_IN = "feature_out"


class OpenStudioLandscapesConfig(enum.StrEnum):
    DEFAULT = "default"
    PRODUCTION = "production"
    DEVELOPMENT = "development"


class FeatureVolumeType(enum.StrEnum):
    """
    CONTAINED means that the data a container produces gets created
        inside a volume that is mounted to directory that lives INSIDE
        a Landscape. New Landscape -> NEW DATA.
    SHARDED means that the data a container produces gets created
        inside a volume that is mounted to directory that lives OUTSIDE
        a Landscape. New Landscape -> EXISTING DATA.
    """

    CONTAINED = "contained"
    SHARED = "shared"


class ComposeScope(enum.StrEnum):
    # Todo:
    #  - [ ] Check if new Compose Scopes need `pip install -e .[dev]`
    INFRASTRUCTURE = "infrastructure"
    DEFAULT = "default"
    LICENSE_SERVER = "license_server"
    WORKER = "worker"


class ComposeCmdExclusion(enum.Enum):
    CMD_APPEND_ALWAYS_EXCLUDE_FROM_QUOTATION = [
        "&&",
        ";",
    ]


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
    LOCAL_REGISTRY = EnvVar("OPENSTUDIOLANDSCAPES__REGISTRY_HOSTNAME").get_value()
    # LOCAL_HARBOR = EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME").get_value()
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
    LOCAL_REGISTRY = {
        "docker_push": True,
        "docker_use_local": False,
        "docker_registry_url": DockerRegistry.LOCAL_REGISTRY,
        "docker_registry_port": EnvVar("OPENSTUDIOLANDSCAPES__REGISTRY_PORT").get_value(),
        "docker_registry_username": EnvVar(
            "OPENSTUDIOLANDSCAPES__REGISTRY_USERNAME"
        ).get_value(),
        "docker_registry_password": EnvVar(
            "OPENSTUDIOLANDSCAPES__REGISTRY_PASSWORD"
        ).get_value(),
        "docker_repository": _REPOSITORY_NAME,
        "docker_repository_type": DockerRepositoryType.PRIVATE,
    }
    # LOCAL_HARBOR = {
    #     # https://github.com/goharbor/harbor
    #     # https://medium.com/@Shamimw/setting-up-harbor-docker-registry-installation-and-pushing-docker-images-a8b3db6fca6a
    #     # Todo
    #     #  - [ ] HTTP is deprecated
    #     "docker_push": True,
    #     "docker_use_local": False,
    #     "docker_registry_url": DockerRegistry.LOCAL_HARBOR,
    #     "docker_registry_port": EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_PORT").get_value(),
    #     "docker_registry_username": EnvVar(
    #         "OPENSTUDIOLANDSCAPES__HARBOR_USERNAME"
    #     ).get_value(),
    #     "docker_registry_password": EnvVar(
    #         "OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD"
    #     ).get_value(),
    #     "docker_repository": _REPOSITORY_NAME,
    #     "docker_repository_type": DockerRepositoryType.PRIVATE,
    # }


class DefaultDicts(enum.Enum):

    """
    This is just a dict blueprint for an individual
    teleport app as documented here:
    https://goteleport.com/docs/reference/deployment/config/#application-service
    """
    TELEPORT_DEFAULT_APP = {
        "name": "",
        "description": "",
        # for ayon specifically, uri could be:
        # "uri": "http://localhost:5005/",
        # "uri": "http://server.farm.evil:5005/",
        # "uri": "192.168.178.195:5005/",
        "uri": "",
        "insecure_skip_verify": False,
        "public_addr": "",
        "use_any_proxy_public_addr": False,
        "rewrite": {
            "redirect": [],
        },
    }
