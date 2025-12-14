from typing import Dict

from dagster import (
AssetsDefinition,
In,
Out,
OpDefinition,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory__CONFIG
from OpenStudioLandscapes.engine.discovery import discovery


def get_feature__CONFIG(
    ASSET_HEADER: Dict,
    CONFIG_STR: str,
    search_model_of_type: discovery.FeatureBaseModel,
) -> AssetsDefinition:

    compose_scope_op__features_in: OpDefinition = factory__CONFIG(
        name=f"op__CONFIG__{ASSET_HEADER['group_name']}",
        CONFIG_STR=CONFIG_STR,
        search_model_of_type=search_model_of_type,
        ins={
            "group_in": In(Dict),
        },
        out={
            "CONFIG": Out(discovery.FeatureBaseModel),
        },
    )

    compose_scope__features_in: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__features_in,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return compose_scope__features_in
