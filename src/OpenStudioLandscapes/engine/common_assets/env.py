from dagster import (
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import op_env


def get_env(
        ASSET_HEADER: dict,
) -> AssetsDefinition:

    env = AssetsDefinition.from_op(
        op_env,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={
            "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
            "constants": AssetKey([*ASSET_HEADER["key_prefix"], "FEATURE_CONFIGS"]),
            "FEATURE_CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "FEATURE_CONFIG"]),
            "COMPOSE_SCOPE": AssetKey([*ASSET_HEADER["key_prefix"], "COMPOSE_SCOPE"]),
            "DOCKER_COMPOSE": AssetKey([*ASSET_HEADER["key_prefix"], "DOCKER_COMPOSE"]),
        },
        keys_by_output_name={
            "env_out": AssetKey([*ASSET_HEADER["key_prefix"], "env"]),
        },
    )

    return env
