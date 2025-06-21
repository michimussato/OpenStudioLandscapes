from dagster import (
    AssetsDefinition,
    AssetKey,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops import factory_feature_out


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
