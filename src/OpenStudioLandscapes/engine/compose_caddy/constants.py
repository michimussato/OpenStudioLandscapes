from typing import Generator, MutableMapping

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.constants import DOCKER_USE_CACHE_GLOBAL


DOCKER_USE_CACHE = DOCKER_USE_CACHE_GLOBAL or False


GROUP = f"Compose_{ComposeScope.CADDY}"
KEY = [GROUP]

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
    "compute_kind": "python",
}

ENVIRONMENT = {
    "CADDY_HOSTNAME": "caddy.farm.evil",
    "CADDY_ADMIN": "",
    "CADDY_PASSWORD": "",
    "CADDY_PORT": 80,
}


@asset(
    **ASSET_HEADER,
    description="",
)
def constants_caddy(
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
