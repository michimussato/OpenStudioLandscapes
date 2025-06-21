from dagster import (
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import op_constants


def get_constants(
        ASSET_HEADER: dict,
) -> AssetsDefinition:

    constants = AssetsDefinition.from_op(
        op_constants,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={
            "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
            "NAME": AssetKey([*ASSET_HEADER["key_prefix"], "NAME"]),
        },
        keys_by_output_name={
            "COMPOSE_SCOPE": AssetKey([*ASSET_HEADER["key_prefix"], "COMPOSE_SCOPE"]),
            "FEATURE_CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "FEATURE_CONFIG"]),
        },
    )

    return constants
