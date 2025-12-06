from dagster import (
    AssetKey,
    AssetsDefinition,
)

from OpenStudioLandscapes.engine.base.ops import op_group_out_compose_scope


def get_group_out(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    group_out = AssetsDefinition.from_op(
        op_group_out_compose_scope,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_output_name={
            "group_out": AssetKey([*ASSET_HEADER["key_prefix"], "group_out"]),
            "compose_project_name": AssetKey(
                [*ASSET_HEADER["key_prefix"], "compose_project_name"]
            ),
            "docker_compose_commands": AssetKey(
                [*ASSET_HEADER["key_prefix"], "docker_compose_commands"]
            ),
        },
        keys_by_input_name={
            "compose": AssetKey([*ASSET_HEADER["key_prefix"], "compose"]),
            "features_in": AssetKey([*ASSET_HEADER["key_prefix"], "features_in"]),
            "cmd_extend": AssetKey([*ASSET_HEADER["key_prefix"], "cmd_extend"]),
            "cmd_append": AssetKey([*ASSET_HEADER["key_prefix"], "cmd_append"]),
            "CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        },
    )

    return group_out
