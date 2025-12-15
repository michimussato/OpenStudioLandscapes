from typing import Union, Dict, List

from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_group_in, factory_feature_in
# from OpenStudioLandscapes.engine.config.models import FeatureBaseModel
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesBaseOut, OpenStudioLandscapesFeatureIn, \
    OpenStudioLandscapesFeatureOut


# get_base_in ?
# Todo
#  - [ ] Refactor this to "feature_in"
def get_group_in(
    ASSET_HEADER: dict,
    ASSET_HEADER_PARENT: dict,
    # Todo:
    #  - [ ] To accept an input_name here is not very elegant
    input_name: str = "group_out",
) -> AssetsDefinition:

    group_in_op = factory_group_in(
        name=f"op_group_in_{ASSET_HEADER['group_name']}",
        ins={
            input_name: In(dict),
        },
        out={
            "group_in": Out(dict),
        },
    )

    group_in = AssetsDefinition.from_op(
        group_in_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        # key_prefix=ASSET_HEADER["key_prefix"]: This can be deceiving: Prefixes everything on top of all
        # other Prefixes
        keys_by_input_name={
            input_name: AssetKey([*ASSET_HEADER_PARENT["key_prefix"], input_name]),
        },
        keys_by_output_name={
            "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
    )

    return group_in


def get_feature_in(
    ASSET_HEADER: Dict,
    ASSET_HEADER_BASE: Dict,
    # parent_feature_in: Union[None, OpenStudioLandscapesFeatureIn],
    ASSET_HEADER_FEATURE_IN: Dict,
    # ASSET_HEADER_PAPRENTS: List[Dict],
    # Todo:
    #  - [ ] To accept an input_name here is not very elegant
    # input_name: str = "group_out_base",
) -> AssetsDefinition:

    if bool(ASSET_HEADER_FEATURE_IN):
        out_parent = {
            "feature_in_parent": In(OpenStudioLandscapesFeatureOut)
        }

        keys_parent = {
            "feature_in_parent": AssetKey([ASSET_HEADER_FEATURE_IN["key_prefix"], "feature_out"])
        }

    else:
        out_parent = {}
        keys_parent = {}


    group_in_op = factory_feature_in(
        name=f"op_feature_in_{ASSET_HEADER['group_name']}",
        ins={
            "group_out_base": In(OpenStudioLandscapesBaseOut),
            **out_parent,
        },
        out={
            "feature_in": Out(OpenStudioLandscapesFeatureIn),
        },
    )

    group_in = AssetsDefinition.from_op(
        group_in_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        # key_prefix=ASSET_HEADER["key_prefix"]: This can be deceiving: Prefixes everything on top of all
        # other Prefixes
        keys_by_input_name={
            "group_out_base": AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out_base"]),
            **keys_parent,
        },
        keys_by_output_name={
            "feature_in": AssetKey([*ASSET_HEADER["key_prefix"], "feature_in"]),
        },
    )

    return group_in
