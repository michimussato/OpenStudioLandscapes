__all__ = [
    "DOCKER_CONFIG",
    "DOCKER_USE_CACHE_BASE",
    "DOCKER_USE_CACHE_GLOBAL",
    "ASSET_HEADER_BASE_ENV",
    "ASSET_HEADER_BASE",
    "ASSET_HEADER_LANDSCAPE_MAP",
    "ASSET_HEADER_COMPOSE_LICENSE_SERVER",
    "ASSET_HEADER_COMPOSE",
    "ASSET_HEADER_COMPOSE_WORKER",
    "ASSET_HEADER_COMPOSE_LICENSE_SERVER",
    "FEATURES",
]

from typing import Generator, MutableMapping, Any

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import *


DOCKER_CONFIG = DockerConfig.LOCAL_HARBOR
DOCKER_USE_CACHE_GLOBAL = True
DOCKER_USE_CACHE_BASE = DOCKER_USE_CACHE_GLOBAL or False


from OpenStudioLandscapes.engine.compose_license_server import constants as constants_compose_license_server

GROUP_COMPOSE_LICENSE_SERVER= constants_compose_license_server.GROUP
KEY_COMPOSE_LICENSE_SERVER = constants_compose_license_server.KEY
ASSET_HEADER_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ASSET_HEADER
ENVIRONMENT_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ENVIRONMENT
# DOCKER_USE_CACHE_COMPOSE_LICENSE_SERVER = DOCKER_USE_CACHE_GLOBAL or constants_compose_license_server.DOCKER_USE_CACHE


from OpenStudioLandscapes.engine.compose import constants as constants_compose

GROUP_COMPOSE= constants_compose.GROUP
KEY_COMPOSE = constants_compose.KEY
ASSET_HEADER_COMPOSE = constants_compose.ASSET_HEADER
ENVIRONMENT_COMPOSE = constants_compose.ENVIRONMENT
# DOCKER_USE_CACHE_COMPOSE = DOCKER_USE_CACHE_GLOBAL or constants_compose.DOCKER_USE_CACHE


from OpenStudioLandscapes.engine.compose_worker import constants as constants_compose_worker

GROUP_COMPOSE_WORKER= constants_compose_worker.GROUP
KEY_COMPOSE_WORKER = constants_compose_worker.KEY
ASSET_HEADER_COMPOSE_WORKER = constants_compose_worker.ASSET_HEADER
ENVIRONMENT_COMPOSE_WORKER = constants_compose_worker.ENVIRONMENT
# DOCKER_USE_CACHE_COMPOSE_WORKER = DOCKER_USE_CACHE_GLOBAL or constants_compose_worker.DOCKER_USE_CACHE


GROUP_BASE_ENV = "OpenStudioLandscapes_Env"
KEY_BASE_ENV = [GROUP_BASE_ENV]

ASSET_HEADER_BASE_ENV = {
    "group_name": GROUP_BASE_ENV,
    "key_prefix": KEY_BASE_ENV,
}


GROUP_BASE = "OpenStudioLandscapes_Base"
KEY_BASE = [GROUP_BASE]

ASSET_HEADER_BASE = {
    "group_name": GROUP_BASE,
    "key_prefix": KEY_BASE,
}


GROUP_LANDSCAPE_MAP = "Landscape_Map"
KEY_LANDSCAPE_MAP = [GROUP_LANDSCAPE_MAP]

ASSET_HEADER_LANDSCAPE_MAP = {
    "group_name": GROUP_LANDSCAPE_MAP,
    "key_prefix": KEY_LANDSCAPE_MAP,
}

FEATURES: dict[str, dict[str, bool | str | ComposeScope | OpenStudioLandscapesConfig]] = {
    # "OpenStudioLandscapes-Ayn": {
    #     # To test faulty Feature definitions
    #     # Make sure things don't break if misconfigured
    #     "enabled": True,
    #     "module": "OpenStudioLandscapes.Ayn.definitions",
    #     "compose_scope": ComposeScope.DEFAULT,
    #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # },
    "OpenStudioLandscapes-Ayon": {
        "enabled": True,
        "module": "OpenStudioLandscapes.Ayon.definitions",
        "definitions": "OpenStudioLandscapes.Ayon.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Kitsu": {
        "enabled": True,
        "module": "OpenStudioLandscapes.Kitsu.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    "OpenStudioLandscapes-Dagster": {
        "enabled": True,
        "module": "OpenStudioLandscapes.Dagster.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    # "OpenStudioLandscapes-Deadline_10_2": {
    #     "enabled": True,
    #     "module": "OpenStudioLandscapes.Deadline_10_2.definitions",
    #     "compose_scope": ComposeScope.DEFAULT,
    #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # },
    # "OpenStudioLandscapes-Deadline_10_2_Worker": {
    #     "enabled": True,
    #     "module": "OpenStudioLandscapes.Deadline_10_2_Worker.definitions",
    #     "compose_scope": ComposeScope.WORKER,
    #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # },
    "OpenStudioLandscapes-filebrowser": {
        "enabled": True,
        "module": "OpenStudioLandscapes.filebrowser.definitions",
        "compose_scope": ComposeScope.DEFAULT,
        "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    },
    # # "OpenStudioLandscapes-Grafana": {
    # #     "enabled": False,
    # #     "module": "OpenStudioLandscapes.Grafana.definitions",
    # #     "compose_scope": ComposeScope.DEFAULT,
    # #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # # },
    # "OpenStudioLandscapes-SESI_gcc_9_3_Houdini_20": {
    #     "enabled": True,
    #     "module": "OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions",
    #     "compose_scope": ComposeScope.LICENSE_SERVER,
    #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # },
    # "OpenStudioLandscapes-NukeRLM_8": {
    #     "enabled": True,
    #     "module": "OpenStudioLandscapes.NukeRLM_8.definitions",
    #     "compose_scope": ComposeScope.LICENSE_SERVER,
    #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # },
    # # "OpenStudioLandscapes-OpenCue": {
    # #     "enabled": False,
    # #     # error: no health check configured
    # #     "module": "OpenStudioLandscapes.OpenCue.definitions",
    # #     "compose_scope": ComposeScope.DEFAULT,
    # #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # # },
    # # "OpenStudioLandscapes-LikeC4": {
    # #     "enabled": False,
    # #     # error This project's package.json defines "packageManager": "yarn@pnpm@10.6.2". However the current global version of Yarn is 1.22.22.
    # #     "module": "OpenStudioLandscapes.LikeC4.definitions",
    # #     "compose_scope": ComposeScope.DEFAULT,
    # #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # # },
    # "OpenStudioLandscapes-Syncthing": {
    #     "enabled": True,
    #     "module": "OpenStudioLandscapes.Syncthing.definitions",
    #     "compose_scope": ComposeScope.DEFAULT,
    #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # },
    # # "OpenStudioLandscapes-Watchtower": {
    # #     "enabled": False,
    # #     "module": "OpenStudioLandscapes.Watchtower.definitions",
    # #     "compose_scope": ComposeScope.DEFAULT,
    # #     "feature_config": OpenStudioLandscapesConfig.DEFAULT,
    # # },
}


@asset(
    **ASSET_HEADER_BASE_ENV,
    description="",
)
def constants_base(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = {
        "DOCKER_USE_CACHE_BASE": DOCKER_USE_CACHE_BASE,
        "DOCKER_USE_CACHE_GLOBAL": DOCKER_USE_CACHE_GLOBAL,
        "ASSET_HEADER_BASE": ASSET_HEADER_BASE,
    }

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
    description="",
    name="FEATURES",
)
def features(
    context: AssetExecutionContext,
) -> Generator[Output[dict] | AssetMaterialization | Any, None, None]:
    """ """

    global FEATURES

    yield Output(FEATURES)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(FEATURES),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
    description="",
    name="DOCKER_CONFIG",
)
def docker_config(
    context: AssetExecutionContext,
) -> Generator[Output[DockerConfig] | AssetMaterialization | Any, None, None]:
    """ """

    global DOCKER_CONFIG

    yield Output(DOCKER_CONFIG)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "DOCKER_CONFIG": MetadataValue.text(DOCKER_CONFIG.name),
            "value": MetadataValue.json(DOCKER_CONFIG.value),
            "type": MetadataValue.text(str(type(DOCKER_CONFIG))),
        },
    )
