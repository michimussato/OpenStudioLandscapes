import pathlib
from typing import Generator, MutableMapping

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.constants import DOCKER_USE_CACHE_GLOBAL, PREFIX_COMPOSE_SCOPE


DOCKER_USE_CACHE = DOCKER_USE_CACHE_GLOBAL or False


GROUP = f"{PREFIX_COMPOSE_SCOPE}_{str(ComposeScope.DEFAULT)}"
KEY = [GROUP]

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
    # "compute_kind": "python",
}

ENVIRONMENT = {}


@asset(
    **ASSET_HEADER,
    description="",
)
def constants_compose(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = ENVIRONMENT

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )


@asset(
    **ASSET_HEADER,
    description="",
)
def DOCKER_COMPOSE(
    context: AssetExecutionContext,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
    """ """

    docker_compose = pathlib.Path(
        "{DOT_LANDSCAPES}",
        "{LANDSCAPE}",
        f"{ASSET_HEADER['group_name']}__{'_'.join(ASSET_HEADER['key_prefix'])}",
        "__".join(context.asset_key.path),
        "docker_compose",
        "docker-compose.yml",
    )

    yield Output(
        value=docker_compose,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
        },
    )
