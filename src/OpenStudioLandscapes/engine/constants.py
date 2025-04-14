__all__ = [
    "DOCKER_CONFIG",
    "DOCKER_USE_CACHE_BASE",
    "DOCKER_USE_CACHE_GLOBAL",
    "GROUP_BASE_ENV",
    "KEY_BASE_ENV",
    "ASSET_HEADER_BASE_ENV",
    "GROUP_BASE_ENV",
    "GROUP_BASE",
    "KEY_BASE",
    "ASSET_HEADER_BASE",
    "GROUP_LANDSCAPE_MAP",
    "KEY_LANDSCAPE_MAP",
    "ASSET_HEADER_LANDSCAPE_MAP",
    "GROUP_COMPOSE_LICENSE_SERVER",
    "KEY_COMPOSE_LICENSE_SERVER",
    "ASSET_HEADER_COMPOSE_LICENSE_SERVER",
    "GROUP_COMPOSE",
    "KEY_COMPOSE",
    "ASSET_HEADER_COMPOSE",
    "GROUP_COMPOSE_WORKER",
    "KEY_COMPOSE_WORKER",
    "ASSET_HEADER_COMPOSE_WORKER",
    "ASSET_HEADER_COMPOSE_LICENSE_SERVER",
    "THIRD_PARTY",
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
    "compute_kind": "python",
}


GROUP_BASE = "OpenStudioLandscapes_Base"
KEY_BASE = [GROUP_BASE]

ASSET_HEADER_BASE = {
    "group_name": GROUP_BASE,
    "key_prefix": KEY_BASE,
    "compute_kind": "python",
}


GROUP_LANDSCAPE_MAP = "Landscape_Map"
KEY_LANDSCAPE_MAP = [GROUP_LANDSCAPE_MAP]

ASSET_HEADER_LANDSCAPE_MAP = {
    "group_name": GROUP_LANDSCAPE_MAP,
    "key_prefix": KEY_LANDSCAPE_MAP,
    "compute_kind": "python",
}


THIRD_PARTY = [
    {
        # To test faulty Feature definitions
        "enabled": True,
        "module": "OpenStudioLandscapes.Ayn.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Ayon.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Kitsu.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Dagster.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Deadline_10_2.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Deadline_10_2_Worker.definitions",
        "compose_scope": ComposeScope.WORKER,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.filebrowser.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": False,
        "module": "OpenStudioLandscapes.Grafana.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions",
        "compose_scope": ComposeScope.LICENSE_SERVER,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.NukeRLM_8.definitions",
        "compose_scope": ComposeScope.LICENSE_SERVER,
    },
    {
        "enabled": False,
        # error: no health check configured
        "module": "OpenStudioLandscapes.OpenCue.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": False,
        # error This project's package.json defines "packageManager": "yarn@pnpm@10.6.2". However the current global version of Yarn is 1.22.22.
        "module": "OpenStudioLandscapes.LikeC4.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Syncthing.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": False,
        "module": "OpenStudioLandscapes.Watchtower.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
]


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
        "THIRD_PARTY": THIRD_PARTY,
        "DOCKER_CONFIG": DOCKER_CONFIG.value,
        # "DOCKER_CACHE_DIR": DOCKER_CACHE_DIR.as_posix(),
    }

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )
