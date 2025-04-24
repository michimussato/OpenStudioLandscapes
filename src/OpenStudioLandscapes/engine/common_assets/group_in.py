from dagster import (
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import op_group_in


def get_group_in(
        ASSET_HEADER: dict,
        ASSET_HEADER_BASE: dict,
) -> AssetsDefinition:

    group_in = AssetsDefinition.from_op(
        op_group_in,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        # key_prefix=ASSET_HEADER["key_prefix"]: This can be deceiving: Prefixes everything on top of all
        # other Prefixes
        keys_by_input_name={
            "group_out": AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out"]),
        },
        keys_by_output_name={
            "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
    )

    return group_in
