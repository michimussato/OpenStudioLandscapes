from dagster import (
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import op_group_out


def get_group_out(
        ASSET_HEADER: dict,
) -> AssetsDefinition:

    group_out = AssetsDefinition.from_op(
        op_group_out,
        can_subset=True,
        group_name=ASSET_HEADER["group_name"],
        keys_by_output_name={
            "group_out": AssetKey([*ASSET_HEADER["key_prefix"], "group_out"]),
            "compose_project_name": AssetKey(
                [*ASSET_HEADER["key_prefix"], "compose_project_name"]
            ),
            "cmd_docker_compose_up": AssetKey(
                [*ASSET_HEADER["key_prefix"], "cmd_docker_compose_up"]
            ),
        },
        keys_by_input_name={
            "compose": AssetKey([*ASSET_HEADER["key_prefix"], "compose"]),
            "env": AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
            "docker_config": AssetKey([*ASSET_HEADER["key_prefix"], "docker_config"]),
        },
    )

    return group_out
