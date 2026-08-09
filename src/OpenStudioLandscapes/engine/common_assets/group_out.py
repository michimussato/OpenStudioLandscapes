from typing import Dict, Type

from dagster import (
    AssetKey,
    AssetsDefinition,
)

from OpenStudioLandscapes.engine.base.ops import op_group_out
# from OpenStudioLandscapes.engine.config.models import FeatureBaseResource


def get_group_out(
    ASSET_HEADER: Dict,
    # resource: Type[FeatureBaseResource],
) -> AssetsDefinition:

    group_out = AssetsDefinition.from_op(
        op_group_out,
        can_subset=False,
        # Experimental Feature:
        # key_prefix=ASSET_HEADER["key_prefix"],
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={
            "feature_in": AssetKey([*ASSET_HEADER["key_prefix"], "feature_in"]),
            "cmd_extend": AssetKey([*ASSET_HEADER["key_prefix"], "cmd_extend"]),
            "cmd_append": AssetKey([*ASSET_HEADER["key_prefix"], "cmd_append"]),
            # "CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
            # This is merely a dependency than an actual input so that the
            # compose file is created before compose-graph
            # is initiated.
            "compose": AssetKey([*ASSET_HEADER["key_prefix"], "compose"]),
        },
        keys_by_output_name={
            "group_out": AssetKey([*ASSET_HEADER["key_prefix"], "group_out"]),
            "compose_project_name": AssetKey(
                [*ASSET_HEADER["key_prefix"], "compose_project_name"]
            ),
            "docker_compose_commands": AssetKey(
                [*ASSET_HEADER["key_prefix"], "docker_compose_commands"]
            ),
        },
    )

    return group_out
