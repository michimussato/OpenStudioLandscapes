from typing import Generator, MutableMapping

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import *


DOCKER_USE_CACHE = False


GROUP = f"Compose_{ComposeScope.LICENSE_SERVER}"
KEY = [GROUP]

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
    "compute_kind": "python",
}

ENVIRONMENT = {}


@asset(
    **ASSET_HEADER,
    description="",
)
def constants_compose_license_server(
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
