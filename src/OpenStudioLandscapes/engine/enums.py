__all__ = [
    "GroupIn",
    "OpenStudioLandscapesConfig",
    "FeatureVolumeType",
    "ComposeScope",
    "ComposeCmdExclusion",
    "DockerComposeRestartPolicy",
    "DockerComposeDependsOnPolicy",
    "DockerComposePolicies",
    "DockerComposeNetworkMode",
    "DockerRepositoryType",
    # "DockerConfig",
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
    SHARED means that the data a container produces gets created
        inside a volume that is mounted to directory that lives OUTSIDE
        a Landscape. New Landscape -> EXISTING DATA.
    """

    CONTAINED = "contained"
    SHARED = "shared"


class ComposeScope(enum.StrEnum):
    # Todo:
    #  - [ ] Check if new Compose Scopes need `pip install -e .[dev]`
    DEFAULT = "default"
    LICENSE_SERVER = "license_server"
    WORKER = "worker"


class ComposeCmdExclusion(enum.Enum):
    CMD_APPEND_ALWAYS_EXCLUDE_FROM_QUOTATION = [
        "&&",
        ";",
    ]


##################################################################
# Docker Compose Enums


class DockerComposeNetworkMode(enum.StrEnum):
    # https://docs.docker.com/engine/network/
    # Docker Compose Ports settings
    # will be ignored if other than "default"
    #
    # https://docs.docker.com/engine/network/#user-defined-networks
    # With the default configuration, containers attached
    # to the default bridge network have unrestricted network
    # access to each other using container IP
    # addresses. They cannot refer to each other by name.
    #
    # You can create custom, user-defined networks, and
    # connect groups of containers to the same network.
    # Once connected to a user-defined network, containers
    # can communicate with each other using container IP
    # addresses or container names.
    #
    # More ref:
    # - https://docs.docker.com/compose/how-tos/networking/
    # - https://dev.to/lovestaco/how-to-bridge-networks-in-docker-compose-docker-composeyml-1i03
    DEFAULT = "default"  # of type "bridge"; try to avoid this one. Use "bridge" explicitly instead.
    BRIDGE = "bridge"
    HOST = "host"
    NONE = "none"
    OVERLAY = "overlay"
    IPVLAN = "ipvlan"
    MACVLAN = "macvlan"


class DockerComposeRestartPolicy(enum.StrEnum):
    # https://docs.docker.com/engine/containers/start-containers-automatically/#use-a-restart-policy
    ALWAYS = "always"
    NO = "no"
    ON_FAILURE = "on-failure"  # no `max_retries` option yet
    UNLESS_STOPPED = "unless-stopped"


class DockerComposeDependsOnPolicy(enum.StrEnum):
    # https://docs.docker.com/compose/how-tos/startup-order/
    SERVICE_STARTED = "service_started"
    SERVICE_HEALTHY = "service_healthy"
    SERVICE_COMPLETED_SUCCESSFULLY = "service_completed_successfully"


class DockerComposePolicies:
    # https://stackoverflow.com/a/75574517/2207196
    NETWORK_MODE = DockerComposeNetworkMode
    RESTART_POLICY = DockerComposeRestartPolicy
    DEPENDENCY_ON_POLICY = DockerComposeDependsOnPolicy


# Docker Compose Enums
##################################################################


# class DockerRegistry(enum.StrEnum):
#     # NONE = "none"
#     LOCAL_LOCALHOST = "localhost"
#     LOCAL_REGISTRY = EnvVar("OPENSTUDIOLANDSCAPES__REGISTRY_HOSTNAME").get_value()
#     # LOCAL_MINIBOSS = os.environ.get("IP_MASTER", "localhost")


class DockerRepositoryType(enum.StrEnum):
    PUBLIC = "public"
    PRIVATE = "private"


# class DockerConfig(enum.Enum):
#     _REPOSITORY_NAME = "openstudiolandscapes".lower()
#     # Do not:
#     # - repeat special characters multiple times (like "__")
#     # - use capitals in repository names
#     # Todo:
#     #  - [ ] LOCAL_NO_PUSH is NOT SUPPORTED YET. Should it be?
#     #  - [ ] Whether to use http or https
#     LOCALHOST = {
#         # Not used:
#         # "docker_push": False,
#         # "docker_use_local": True,
#         "docker_registry_url": DockerRegistry.LOCAL_LOCALHOST,
#         "docker_registry_port": None,
#         "docker_registry_username": None,
#         "docker_registry_password": None,
#         # "docker_repository": _REPOSITORY_NAME,
#         "docker_repository_type": DockerRepositoryType.PUBLIC,
#     }
#     LOCAL_REGISTRY = {
#         "docker_push": True,  # auto_push ?
#         "docker_use_local": False,
#         "docker_registry_url": DockerRegistry.LOCAL_REGISTRY,
#         "docker_registry_port": EnvVar(
#             "OPENSTUDIOLANDSCAPES__REGISTRY_PORT"
#         ).get_value(),
#         "docker_registry_username": EnvVar(
#             "OPENSTUDIOLANDSCAPES__REGISTRY_USERNAME"
#         ).get_value(),
#         "docker_registry_password": EnvVar(
#             "OPENSTUDIOLANDSCAPES__REGISTRY_PASSWORD"
#         ).get_value(),
#         "docker_repository": _REPOSITORY_NAME,
#         "docker_repository_type": DockerRepositoryType.PRIVATE,
#     }
