from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops import factory_docker_config
from OpenStudioLandscapes.engine.enums import DockerConfig


def get_docker_config(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    docker_config_op = factory_docker_config(
        name=f"op_docker_config_{ASSET_HEADER['group_name']}",
        ins={
            "group_in": In(dict),
        },
        out={
            "docker_config": Out(DockerConfig),
        },
    )

    docker_config = AssetsDefinition.from_op(
        docker_config_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_output_name={
            "docker_config": AssetKey([*ASSET_HEADER["key_prefix"], "docker_config"]),
        },
        keys_by_input_name={
            "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
    )

    return docker_config
