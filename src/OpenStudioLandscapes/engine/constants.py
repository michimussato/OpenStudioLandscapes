__all__ = [
    "DOCKER_CONFIG",
    "DOCKER_USE_CACHE",
    "DOCKER_USE_CACHE_GLOBAL",
    "GROUP_HARBOR",
    "KEY_HARBOR",
    "ASSET_HEADER_HARBOR",
    "ENVIRONMENT_HARBOR",
    "GROUP_BASE",
    "KEY_BASE",
    "ASSET_HEADER_BASE",
    "GROUP_LANDSCAPE_MAP",
    "KEY_LANDSCAPE_MAP",
    "ASSET_HEADER_LANDSCAPE_MAP",
    "GROUP_COMPOSE",
    "KEY_COMPOSE",
    "ASSET_HEADER_COMPOSE",
    "GROUP_COMPOSE_WORKER",
    "KEY_COMPOSE_WORKER",
    "ASSET_HEADER_COMPOSE_WORKER",
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
DOCKER_USE_CACHE = DOCKER_USE_CACHE_GLOBAL or False


GROUP_HARBOR = f"Compose_{ComposeScope.HARBOR}"
KEY_HARBOR = [GROUP_HARBOR]

ASSET_HEADER_HARBOR = {
    "group_name": GROUP_HARBOR,
    "key_prefix": KEY_HARBOR,
    "compute_kind": "python",
}

ENVIRONMENT_HARBOR = {
    "HARBOR_ADMIN": "admin",
    "HARBOR_PASSWORD": "Harbor12345",
}


GROUP_BASE = "Base"
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


GROUP_COMPOSE = f"Compose_{ComposeScope.DEFAULT}"
KEY_COMPOSE = [GROUP_COMPOSE]

ASSET_HEADER_COMPOSE = {
    "group_name": GROUP_COMPOSE,
    "key_prefix": KEY_COMPOSE,
    "compute_kind": "python",
}


GROUP_COMPOSE_WORKER = f"Compose_{ComposeScope.WORKER}"
KEY_COMPOSE_WORKER = [GROUP_COMPOSE_WORKER]

ASSET_HEADER_COMPOSE_WORKER = {
    "group_name": GROUP_COMPOSE_WORKER,
    "key_prefix": KEY_COMPOSE_WORKER,
    "compute_kind": "python",
}


THIRD_PARTY = [
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Ayon.definitions",
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
        "module": "OpenStudioLandscapes.Kitsu.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
    # {
    #     "enabled": False,
    #     # error: no health check configured
    #     "module": "OpenStudioLandscapes.OpenCue.definitions",
    #     "compose_scope": ComposeScope.DEFAULT,
    # },
    # {
    #     "enabled": False,
    #     # error This project's package.json defines "packageManager": "yarn@pnpm@10.6.2". However the current global version of Yarn is 1.22.22.
    #     "module": "OpenStudioLandscapes.LikeC4.definitions",
    #     "compose_scope": ComposeScope.DEFAULT,
    # },
    {
        "enabled": True,
        "module": "OpenStudioLandscapes.Syncthing.definitions",
        "compose_scope": ComposeScope.DEFAULT,
    },
]


@asset(
    name=f"constants_{GROUP_HARBOR}",
    group_name="Constants",
    key_prefix=KEY_HARBOR,
    compute_kind="python",
    description="",
)
def constants_harbor(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = ENVIRONMENT_HARBOR
    # {
    #     "HARBOR_ADMIN": "admin",
    #     "HARBOR_PASSWORD": "Harbor12345",
    # }

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )


@asset(
    name=f"constants_{GROUP_BASE}",
    group_name="Constants",
    key_prefix=KEY_BASE,
    compute_kind="python",
    description="",
)
def constants_base(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = {
        "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
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


@asset(
    name=f"constants_{GROUP_COMPOSE}",
    group_name="Constants",
    key_prefix=KEY_COMPOSE,
    compute_kind="python",
    description="",
)
def constants_compose(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = {
        "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
        "ASSET_HEADER_COMPOSE": ASSET_HEADER_COMPOSE,
        "THIRD_PARTY": THIRD_PARTY,
    }

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )


@asset(
    name=f"constants_{GROUP_COMPOSE_WORKER}",
    group_name="Constants",
    key_prefix=KEY_COMPOSE_WORKER,
    compute_kind="python",
    description="",
)
def constants_compose_worker(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = {
        "DOCKER_USE_CACHE": DOCKER_USE_CACHE,
        "ASSET_HEADER_COMPOSE": ASSET_HEADER_COMPOSE_WORKER,
        "THIRD_PARTY": THIRD_PARTY,
    }

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )
