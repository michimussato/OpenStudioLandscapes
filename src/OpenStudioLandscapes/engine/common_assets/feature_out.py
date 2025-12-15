from typing import Dict

from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out, OpDefinition,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_feature_out, factory_feature_out_v2
from OpenStudioLandscapes.engine.discovery import discovery
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesFeatureOut


def get_feature_out(
    ASSET_HEADER: dict,
    feature_out_ins: dict,
) -> AssetsDefinition:

    feature_out_ins_op = {}
    feature_out_ins_asset = {}
    for k, v in feature_out_ins.items():
        feature_out_ins_op[k] = In(v)
        feature_out_ins_asset[k] = AssetKey([*ASSET_HEADER["key_prefix"], k])

    feature_out_op = factory_feature_out(
        name=f"op_feature_out_{ASSET_HEADER['group_name']}",
        ins=feature_out_ins_op,
        out={
            "feature_out": Out(dict),
        },
    )

    feature_out = AssetsDefinition.from_op(
        feature_out_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_output_name={
            "feature_out": AssetKey([*ASSET_HEADER["key_prefix"], "feature_out"]),
        },
        keys_by_input_name=feature_out_ins_asset,
    )

    return feature_out


def get_feature_out_v2(
    ASSET_HEADER: Dict,
    # feature_out_ins: Dict,
) -> AssetsDefinition:

    # feature_out_ins_op = {}
    # feature_out_ins_asset = {}
    # for k, v in feature_out_ins.items():
    #     feature_out_ins_op[k] = In(v)
    #     feature_out_ins_asset[k] = AssetKey([*ASSET_HEADER["key_prefix"], k])

    feature_out_op: OpDefinition = factory_feature_out_v2(
        name=f"op_feature_out_v2_{ASSET_HEADER['group_name']}",
        # ins=feature_out_ins_op,
        ins={
            # "compose_networks": In(dict),
            "compose": In(Dict),
            "CONFIG": In(discovery.FeatureBaseModel),
            # "group_in": In(dict)
        },
        out={
            "feature_out_v2": Out(OpenStudioLandscapesFeatureOut),
        },
    )

    feature_out: AssetsDefinition = AssetsDefinition.from_op(
        feature_out_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={},
        keys_by_output_name={
            # "feature_out": AssetKey([*ASSET_HEADER["key_prefix"], "feature_out"]),
        },
    )

    return feature_out
