import enum
from typing import TypedDict, Any, Dict, List, LiteralString, Required, NotRequired
from OpenStudioLandscapes.engine.enums import ComposeNetworkMode, ComposeScope

__all__ = [
    "get_pangolin_newt_service_skeleton",
]



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


# class Environment(TypedDict):
#     environment: Dict[LiteralString, Any]


# class Volume(TypedDict, total=False):
#     volume: Required[LiteralString]

# class VolumeList(TypedDict, total=False):
#     volumes: List[Volume]


class DockerComposeServiceDefinition(TypedDict, total=False):
    environment: Dict[LiteralString, Any]
    container_name: Required[LiteralString]
    image: Required[LiteralString]
    volumes: List[LiteralString]
    networks: List[LiteralString]
    ports: List[LiteralString]
    network_mode: ComposeNetworkMode
    restart: DockerComposeRestartPolicy


# class DockerComposeService(TypedDict, total=False):
#     # service_name: Required[LiteralString]
#     service_definition: Required[DockerComposeServiceDefinition]
#     volumes: List[Volume]


class _DockerComposeNetworkNiceName(TypedDict, total=False):
    name: Required[LiteralString]


class DockerComposeNetworkDefinition(TypedDict, total=False):
    name: Required[Dict[str, _DockerComposeNetworkNiceName]]


# class PangolinSite(TypedDict):
#     service: Required[DockerComposeService]
#     network: DockerComposeNetworkDefinition


# _is_this_valid: DockerComposeServiceDefinition = {
#     "image": "docker.io/fosrl/newt",
#     "restart": DockerComposeRestartPolicy.ALWAYS,
#     "ports": [
#         "8080:80"
#     ],
#     "container_name": "newt",
#     "environment": {
#         "PANGOLIN_ENDPOINT": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__PANGOLIN_ENDPOINT}" % compose_scope.upper(),
#         "NEWT_ID": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__NEWT_ID}" % compose_scope.upper(),
#         "NEWT_SECRET": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__NEWT_SECRET}" % compose_scope.upper(),
#         # "ACCEPT_CLIENTS": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__ACCEPT_CLIENTS}" % compose_scope.upper(),
#         "ACCEPT_CLIENTS": True,
#         "DOCKER_SOCKET": "/var/run/docker.sock",
#     },
#     "volumes": [
#         "/var/run/docker.sock:/var/run/docker.sock",
#     ]
# }

# network: DockerComposeNetworkDefinition = {
#     "name": {
#         "default": "pangolin_default",
#     },
# }

# Services


def get_pangolin_newt_service_skeleton(
    compose_scope: ComposeScope,
) -> DockerComposeServiceDefinition:
    _service: DockerComposeServiceDefinition = {
        "image": "docker.io/fosrl/newt",
        "container_name": "newt",
        "restart": DockerComposeRestartPolicy.ALWAYS,
        "environment": {
            "PANGOLIN_ENDPOINT": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__PANGOLIN_ENDPOINT}" % compose_scope.upper(),
            "NEWT_ID": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_ID}" % compose_scope.upper(),
            "NEWT_SECRET": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_SECRET}" % compose_scope.upper(),
            # "ACCEPT_CLIENTS": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__ACCEPT_CLIENTS}" % compose_scope.upper(),
            "ACCEPT_CLIENTS": True,
            "DOCKER_SOCKET": "/var/run/docker.sock",
        },
        "volumes": [
            "/var/run/docker.sock:/var/run/docker.sock",
        ],
        "networks": []
    }

    return _service