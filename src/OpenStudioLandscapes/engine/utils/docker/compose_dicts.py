from typing import Any, Dict, List, LiteralString, Required, TypedDict

from OpenStudioLandscapes.engine.enums import *

__all__ = [
    "get_pangolin_newt_service_skeleton",
]


# This is a WIP file (messy) and we'll try to
# extend it as we go - it will bring a bit
# more structure and guidance for Docker and
# Compose files


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
    network_mode: DockerComposeNetworkMode
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


# # YAML StrEnum representer
# # ------------------------
# # Using yaml.dump on StrEnums results in the following object representation:
# #     restart: !!python/object/apply:OpenStudioLandscapes.engine.utils.docker.compose_dicts.DockerComposeRestartPolicy
# #     - always
# #
# # Which will result in the following error:
# # yaml.constructor.ConstructorError: could not determine a constructor for the tag 'tag:yaml.org,2002:python/object/apply:OpenStudioLandscapes.engine.utils.docker.compose_dicts.DockerComposeRestartPolicy'
# #   in "/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-11-19-02-46-18-512b89c22d304baf9ba32f281b1fbe36/ComposeScope_worker__ComposeScope_worker/ComposeScope_worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml", line 20, column 14
# #
# # yaml.safe_dump requires for an object to be represented in a proper way
# # Reference: https://techoverflow.net/2024/01/07/how-to-fix-python-yaml-namedtuple-error-yaml-representer-representererror-cannot-represent-an-object/
# def represent_strenum(
#         dumper,
#         data: DockerComposeRestartPolicy,
# ):
#     return dumper.represent_dict(data.value)


# Services


def get_pangolin_newt_service_skeleton(
    compose_scope: ComposeScope,
) -> DockerComposeServiceDefinition:
    _service: DockerComposeServiceDefinition = {
        "image": "docker.io/fosrl/newt",
        "container_name": "newt",
        "restart": DockerComposePolicies.RESTART_POLICY.ALWAYS,
        "environment": {
            "PANGOLIN_ENDPOINT": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__PANGOLIN_ENDPOINT}"
            % compose_scope.upper(),
            "NEWT_ID": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_ID}"
            % compose_scope.upper(),
            "NEWT_SECRET": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_%s__NEWT_SECRET}"
            % compose_scope.upper(),
            # "ACCEPT_CLIENTS": "${OPENSTUDIOLANDSCAPES__PANGOLIN_SITE_%s__ACCEPT_CLIENTS}" % compose_scope.upper(),
            "ACCEPT_CLIENTS": True,
            "DOCKER_SOCKET": "/var/run/docker.sock",
        },
        "volumes": [
            "/var/run/docker.sock:/var/run/docker.sock",
        ],
        "networks": [],
    }

    return _service
