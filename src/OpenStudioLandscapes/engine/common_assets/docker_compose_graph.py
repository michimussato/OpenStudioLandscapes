from dagster import (
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import op_docker_compose_graph


def get_docker_compose_graph(
        ASSET_HEADER: dict,
) -> AssetsDefinition:

    docker_compose_graph = AssetsDefinition.from_op(
        op_docker_compose_graph,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={
            "group_out": AssetKey([*ASSET_HEADER["key_prefix"], "group_out"]),
            "compose_project_name": AssetKey(
                [*ASSET_HEADER["key_prefix"], "compose_project_name"]
            ),
        },
    )

    return docker_compose_graph
