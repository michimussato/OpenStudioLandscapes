from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_compose
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

# Todo:
#  - compose_map factory


def get_compose(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    compose_op = factory_compose(
        name=f"op_compose_{ASSET_HEADER['group_name']}",
        ins={
            "compose_networks": In(dict),
            "compose_maps": In(list),
            "CONFIG": In(FeatureBaseModel),
            # "group_in": In(dict)
        },
        out={
            "compose": Out(dict),
        },
    )

    compose = AssetsDefinition.from_op(
        compose_op,
        # Todo:
        #  - [ ] Change to AssetKey
        tags_by_output_name={
            "compose": {
                "compose": "third_party",
            },
        },
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={
            "compose_networks": AssetKey(
                [*ASSET_HEADER["key_prefix"], "compose_networks"]
            ),
            "compose_maps": AssetKey([*ASSET_HEADER["key_prefix"], "compose_maps"]),
            "CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
            # "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
    )

    return compose
