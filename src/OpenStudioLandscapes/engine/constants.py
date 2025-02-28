__all__ = [
    "DOCKER_USE_CACHE",
    "DOCKER_USE_CACHE_GLOBAL",
    "GROUP_BASE",
    "GROUP_COMPOSE",
    "KEY_BASE",
    "KEY_COMPOSE",
    "ASSET_HEADER_BASE",
    "ASSET_HEADER_COMPOSE",
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

DOCKER_USE_CACHE = False
DOCKER_USE_CACHE_GLOBAL = False


GROUP_BASE = "Base"
KEY_BASE = [GROUP_BASE]

ASSET_HEADER_BASE = {
    "group_name": GROUP_BASE,
    "key_prefix": KEY_BASE,
    "compute_kind": "python",
}


GROUP_COMPOSE = "Compose"
KEY_COMPOSE = [GROUP_COMPOSE]

ASSET_HEADER_COMPOSE = {
    "group_name": GROUP_COMPOSE,
    "key_prefix": KEY_COMPOSE,
    "compute_kind": "python",
}


THIRD_PARTY = [
    "OpenStudioLandscapes.Ayon.definitions",
    "OpenStudioLandscapes.Dagster.definitions",
    "OpenStudioLandscapes.Deadline_10_2.definitions",
    "OpenStudioLandscapes.filebrowser.definitions",
    "OpenStudioLandscapes.Grafana.definitions",
    "OpenStudioLandscapes.Kitsu.definitions",
    "OpenStudioLandscapes.OpenCue.definitions",
    "OpenStudioLandscapes.LikeC4.definitions",  # Errors atm; minor issue
]


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
