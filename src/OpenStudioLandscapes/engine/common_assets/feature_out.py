from typing import Dict, List, Type

from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    OpDefinition,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import (
    factory_feature_out_v2,
)
from OpenStudioLandscapes.engine.config.models import FeatureBaseResource
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesFeatureOut


def get_feature_out_v2(
    ASSET_HEADER: Dict,
    resource: Type[FeatureBaseResource],
) -> AssetsDefinition:

    feature_out_op: OpDefinition = factory_feature_out_v2(
        name=f"op_feature_out_v2_{ASSET_HEADER['group_name']}",
        resource=resource,
        ins={
            "compose": In(Dict),
            "cmd_extend": In(List),
            "cmd_append": In(Dict),
        },
        out={
            "feature_out_v2": Out(OpenStudioLandscapesFeatureOut),
        },
    )

    feature_out: AssetsDefinition = AssetsDefinition.from_op(
        feature_out_op,
        # Experimental Feature:
        # key_prefix=ASSET_HEADER["key_prefix"],
        group_name=ASSET_HEADER["group_name"],
        can_subset=False,
        keys_by_input_name={
            "compose": AssetKey([*ASSET_HEADER["key_prefix"], "compose"]),
            "cmd_extend": AssetKey([*ASSET_HEADER["key_prefix"], "cmd_extend"]),
            "cmd_append": AssetKey([*ASSET_HEADER["key_prefix"], "cmd_append"]),
        },
        keys_by_output_name={
            "feature_out_v2": AssetKey([*ASSET_HEADER["key_prefix"], "feature_out_v2"]),
        },
    )

    return feature_out
