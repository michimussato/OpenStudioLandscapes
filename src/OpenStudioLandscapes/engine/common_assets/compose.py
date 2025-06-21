from dagster import (
    In,
    Out,
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import factory_compose


def get_compose(
        ASSET_HEADER: dict,
) -> AssetsDefinition:

    compose_op = factory_compose(
        name=f"op_compose_{ASSET_HEADER['group_name']}",
        ins={
            "compose_networks": In(dict),
            "compose_maps": In(list),
            "env": In(dict),
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
            "compose_networks": AssetKey([*ASSET_HEADER["key_prefix"], "compose_networks"]),
            "compose_maps": AssetKey([*ASSET_HEADER["key_prefix"], "compose_maps"]),
            "env": AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        },
    )

    return compose
