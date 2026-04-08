from typing import Dict, Type

from dagster import (
    AssetsDefinition,
    In,
    OpDefinition,
    Out,
)

# from OpenStudioLandscapes.engine.base.ops.factories import factory__CONFIG
# from OpenStudioLandscapes.engine.discovery import discovery
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesFeatureIn


# def get_feature__CONFIG(
#     ASSET_HEADER: Dict,
#     CONFIG_STR: str,
#     search_model_of_type: Type[discovery.FeatureBaseModel],
# ) -> AssetsDefinition:
#
#     feature_in_op__CONFIG: OpDefinition = factory__CONFIG(
#         name=f"op__CONFIG__{ASSET_HEADER['group_name']}",
#         CONFIG_STR=CONFIG_STR,
#         search_model_of_type=search_model_of_type,
#         ins={
#             "feature_in": In(OpenStudioLandscapesFeatureIn),
#         },
#         out={
#             "CONFIG": Out(discovery.FeatureBaseModel),
#             # Todo:
#             #  - [ ] Can we do this dynamically based on whether there is a parent?
#             # "CONFIG_PARENT": Out(discovery.FeatureBaseModel),
#         },
#     )
#
#     feature_in__CONFIG: AssetsDefinition = AssetsDefinition.from_op(
#         feature_in_op__CONFIG,
#         group_name=ASSET_HEADER["group_name"],
#         key_prefix=ASSET_HEADER["key_prefix"],
#         keys_by_input_name={},
#         keys_by_output_name={},
#     )
#
#     return feature_in__CONFIG
