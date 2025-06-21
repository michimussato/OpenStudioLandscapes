from dagster import (
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import op_docker_config_json


def get_docker_config_json(
        ASSET_HEADER: dict,
) -> AssetsDefinition:

    docker_config_json = AssetsDefinition.from_op(
        op_docker_config_json,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={
            "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
        keys_by_output_name={
            "docker_config_json": AssetKey([*ASSET_HEADER["key_prefix"], "docker_config_json"]),
        },
    )

    return docker_config_json
