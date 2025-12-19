from typing import Dict, Type, Union

from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import (
    factory_feature_in,
    factory_feature_in_parent,
    factory_group_in,
)
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel
from OpenStudioLandscapes.engine.link.models import (
    OpenStudioLandscapesBaseOut,
    OpenStudioLandscapesFeatureIn,
    OpenStudioLandscapesFeatureOut,
)


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
    ASSET_HEADER_FEATURE_IN: Dict,
) -> AssetsDefinition:

    if bool(ASSET_HEADER_FEATURE_IN):
        out_parent = {"feature_in_parent": In(OpenStudioLandscapesFeatureOut)}

        keys_parent = {
            "feature_in_parent": AssetKey(
                [*ASSET_HEADER_FEATURE_IN["key_prefix"], "feature_out_v2"]
            )
        }

    else:
        out_parent = {}
        keys_parent = {}

    feature_in_op = factory_feature_in(
        name=f"op_feature_in_{ASSET_HEADER['group_name']}",
        ins={
            "group_out_base": In(OpenStudioLandscapesBaseOut),
            **out_parent,
        },
        out={
            "feature_in": Out(OpenStudioLandscapesFeatureIn),
        },
    )

    feature_in = AssetsDefinition.from_op(
        feature_in_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={
            "group_out_base": AssetKey(
                [*ASSET_HEADER_BASE["key_prefix"], "group_out_base"]
            ),
            **keys_parent,
        },
        keys_by_output_name={
            "feature_in": AssetKey([*ASSET_HEADER["key_prefix"], "feature_in"]),
        },
    )

    return feature_in


def get_feature_in_parent(
    ASSET_HEADER: Dict,
    config_parent: Union[None, Type[FeatureBaseModel]],
) -> Union[AssetsDefinition, None]:

    # Do not produce the assets
    # if there is no parent config
    if config_parent is None:
        return None

    feature_in_parent_op = factory_feature_in_parent(
        name=f"op_feature_in_parent_{ASSET_HEADER['group_name']}",
        CONFIG_PARENT=config_parent,
        ins={
            "feature_in": In(OpenStudioLandscapesFeatureIn),
        },
        out={
            "feature_in_parent": Out(OpenStudioLandscapesFeatureOut),
            "CONFIG_PARENT": Out(FeatureBaseModel),
        },
    )

    feature_in_parent = AssetsDefinition.from_op(
        feature_in_parent_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={
            "feature_in": AssetKey([*ASSET_HEADER["key_prefix"], "feature_in"]),
        },
        keys_by_output_name={
            "feature_in_parent": AssetKey(
                [*ASSET_HEADER["key_prefix"], "feature_in_parent"]
            ),
            "CONFIG_PARENT": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG_PARENT"]),
        },
    )

    return feature_in_parent
