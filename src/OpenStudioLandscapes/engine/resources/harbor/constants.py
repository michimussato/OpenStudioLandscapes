__all__ = [
    # "PREFIX_COMPOSE_SCOPE",
    # "DOCKER_CONFIG",
    # "DOCKER_USE_CACHE_BASE",
    # "DOCKER_USE_CACHE_GLOBAL",
    "ASSET_HEADER_RESOURCE_HARBOR",
    # "DOCKER_PROGRESS",
]

from typing import Generator, MutableMapping

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.features import (  # used in OpenStudioLandscapes.engine.discovery.discovery
    FEATURES,
)

# DOCKER_PROGRESS = [
#     "auto",
#     "quiet",
#     "plain",
#     "tty",
#     "rawjson",
# ][2]


# DOCKER_CONFIG = DockerConfig.LOCAL_HARBOR
# DOCKER_USE_CACHE_GLOBAL = False
# DOCKER_USE_CACHE_BASE = DOCKER_USE_CACHE_GLOBAL or False
# PREFIX_COMPOSE_SCOPE = "ComposeScope"


# from OpenStudioLandscapes.engine.compose_scopes.default import (
#     constants as constants_compose,
# )
#
# GROUP_COMPOSE = constants_compose.GROUP
# KEY_COMPOSE = constants_compose.KEY
# ASSET_HEADER_COMPOSE = constants_compose.ASSET_HEADER
# ENVIRONMENT_COMPOSE = constants_compose.ENVIRONMENT


# from OpenStudioLandscapes.engine.compose_scopes.license_server import (
#     constants as constants_compose_license_server,
# )
#
# GROUP_COMPOSE_LICENSE_SERVER = constants_compose_license_server.GROUP
# KEY_COMPOSE_LICENSE_SERVER = constants_compose_license_server.KEY
# ASSET_HEADER_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ASSET_HEADER
# ENVIRONMENT_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ENVIRONMENT


# from OpenStudioLandscapes.engine.compose_scopes.teleport import (
#     constants as constants_compose_teleport,
# )
#
# GROUP_COMPOSE_TELEPORT = constants_compose_teleport.GROUP
# KEY_COMPOSE_TELEPORT = constants_compose_teleport.KEY
# ASSET_HEADER_COMPOSE_TELEPORT = constants_compose_teleport.ASSET_HEADER
# ENVIRONMENT_COMPOSE_TELEPORT = constants_compose_teleport.ENVIRONMENT


# from OpenStudioLandscapes.engine.compose_scopes.worker import (
#     constants as constants_compose_worker,
# )
#
# GROUP_COMPOSE_WORKER = constants_compose_worker.GROUP
# KEY_COMPOSE_WORKER = constants_compose_worker.KEY
# ASSET_HEADER_COMPOSE_WORKER = constants_compose_worker.ASSET_HEADER
# ENVIRONMENT_COMPOSE_WORKER = constants_compose_worker.ENVIRONMENT


GROUP_RESOURCE_HARBOR = "OpenStudioLandscapes_Resource_Harbor"
KEY_RESOURCE_HARBOR = [GROUP_RESOURCE_HARBOR]

ASSET_HEADER_RESOURCE_HARBOR = {
    "group_name": GROUP_RESOURCE_HARBOR,
    "key_prefix": KEY_RESOURCE_HARBOR,
}


# GROUP_BASE = "OpenStudioLandscapes_Base"
# KEY_BASE = [GROUP_BASE]
#
# ASSET_HEADER_BASE = {
#     "group_name": GROUP_BASE,
#     "key_prefix": KEY_BASE,
# }


# GROUP_LANDSCAPE_MAP = "Landscape_Map"
# KEY_LANDSCAPE_MAP = [GROUP_LANDSCAPE_MAP]
#
# ASSET_HEADER_LANDSCAPE_MAP = {
#     "group_name": GROUP_LANDSCAPE_MAP,
#     "key_prefix": KEY_LANDSCAPE_MAP,
# }


# GROUP_DISTRIBUTABLE = "Distributable"
# KEY_DISTRIBUTABLE = [GROUP_DISTRIBUTABLE]
#
# ASSET_HEADER_DISTRIBUTABLE = {
#     "group_name": GROUP_DISTRIBUTABLE,
#     "key_prefix": KEY_DISTRIBUTABLE,
# }


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    description="",
)
def constants_resource_harbor(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = {
        # "DOCKER_USE_CACHE_BASE": DOCKER_USE_CACHE_BASE,
        # "DOCKER_USE_CACHE_GLOBAL": DOCKER_USE_CACHE_GLOBAL,
        "ASSET_HEADER_BASE": ASSET_HEADER_RESOURCE_HARBOR,
    }

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )


# @asset(
#     **ASSET_HEADER_BASE_ENV,
#     description="",
#     name="FEATURES",
# )
# def features(
#     context: AssetExecutionContext,
# ) -> Generator[Output[dict] | AssetMaterialization | Any, None, None]:
#     """ """
#
#     global FEATURES
#
#     yield Output(FEATURES)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(FEATURES),
#         },
#     )


# @asset(
#     **ASSET_HEADER_BASE_ENV,
#     description="",
#     name="DOCKER_CONFIG",
# )
# def docker_config(
#     context: AssetExecutionContext,
# ) -> Generator[Output[DockerConfig] | AssetMaterialization | Any, None, None]:
#     """ """
#
#     global DOCKER_CONFIG
#
#     yield Output(DOCKER_CONFIG)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "DOCKER_CONFIG": MetadataValue.text(DOCKER_CONFIG.name),
#             "value": MetadataValue.json(DOCKER_CONFIG.value),
#             "type": MetadataValue.text(str(type(DOCKER_CONFIG))),
#         },
#     )
