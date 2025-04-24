from dagster import (
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import op_compose


def get_compose(
        ASSET_HEADER: dict,
) -> AssetsDefinition:

    compose = AssetsDefinition.from_op(
        op_compose,
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
            "compose_networks": AssetKey([*ASSET_HEADER["key_prefix"], "compose_networks"]),
            "compose_maps": AssetKey([*ASSET_HEADER["key_prefix"], "compose_maps"]),
            "env": AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        },
    )

    return compose
