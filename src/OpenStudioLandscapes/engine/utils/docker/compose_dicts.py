import enum
from typing import TypedDict, Any, Dict, List, LiteralString, Required
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
    # restart: DockerComposeRestartPolicy


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
        # "restart": DockerComposeRestartPolicy.ALWAYS,
        # Results in:
        #     restart: !!python/object/apply:OpenStudioLandscapes.engine.utils.docker.compose_dicts.DockerComposeRestartPolicy
        #     - always
        # yaml.constructor.ConstructorError: could not determine a constructor for the tag 'tag:yaml.org,2002:python/object/apply:OpenStudioLandscapes.engine.utils.docker.compose_dicts.DockerComposeRestartPolicy'
        #   in "/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-11-19-02-46-18-512b89c22d304baf9ba32f281b1fbe36/ComposeScope_worker__ComposeScope_worker/ComposeScope_worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml", line 20, column 14
        #
        # Stack Trace:
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/utils.py", line 56, in op_execution_error_boundary
        #     yield
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_utils/__init__.py", line 480, in iterate_with_context
        #     next_output = next(iterator)
        #                   ^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/base/ops/__init__.py", line 693, in op_docker_compose_graph
        #     trees = dcg.parse_docker_compose(pathlib.Path(group_out))
        #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/docker_compose_graph/docker_compose_graph.py", line 346, in parse_docker_compose
        #     docker_compose_chainmap: dict = pyyaml.full_load(fr)
        #                                     ^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/__init__.py", line 105, in full_load
        #     return load(stream, FullLoader)
        #            ^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/__init__.py", line 81, in load
        #     return loader.get_single_data()
        #            ^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/constructor.py", line 51, in get_single_data
        #     return self.construct_document(node)
        #            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/constructor.py", line 60, in construct_document
        #     for dummy in generator:
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/constructor.py", line 413, in construct_yaml_map
        #     value = self.construct_mapping(node)
        #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/constructor.py", line 218, in construct_mapping
        #     return super().construct_mapping(node, deep=deep)
        #            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/constructor.py", line 143, in construct_mapping
        #     value = self.construct_object(value_node, deep=deep)
        #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/constructor.py", line 100, in construct_object
        #     data = constructor(self, node)
        #            ^^^^^^^^^^^^^^^^^^^^^^^
        #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/yaml/constructor.py", line 427, in construct_undefined
        #     raise ConstructorError(None, None,
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