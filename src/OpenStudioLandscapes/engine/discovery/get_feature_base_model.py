from typing import Dict, List, Type, Union

from dagster import (
    AssetExecutionContext,
    OpExecutionContext,
)

from OpenStudioLandscapes.engine.discovery import discovery


# def get_feature_base_model(
#     context: Union[OpExecutionContext, AssetExecutionContext],
#     discovered_models: Dict[str, discovery.OpenStudioLandscapesDiscoveredFeature],
#     search_instance_type: Type[discovery.FeatureBaseModel],
# ) -> discovery.FeatureBaseModel:
#     """
#     We are not create a new Config object for this Feature. It
#     was pre-made during the bootstrapping process.
#     We just need to find it in the `discovery.DISCOVERED_MODELS` dict.
#
#     Find the `OpenStudioLandscapes.engine.config.models.FeatureBaseModel`
#     from the discovered models that matches the package name and
#     return its Config object.
#
#     As all Feature Config objects are subclasses of
#     `OpenStudioLandscapes.engine.config.models.FeatureBaseModel`
#     and also singletons, there will always only be one Config object of type
#     <search_instance_type>.
#
#     Returns:
#         Config Subclass of `OpenStudioLandscapes.engine.config.models.FeatureBaseModel`
#
#     Raises:
#         AssertionError
#     """
#
#     def filter_feature_config(
#         value: discovery.OpenStudioLandscapesDiscoveredFeature,
#     ):
#         feature_config: discovery.FeatureBaseModel = value.config
#         if isinstance(feature_config, search_instance_type):
#             return True
#         else:
#             return False
#
#     matches: List[discovery.FeatureBaseModel] = list(
#         filter(filter_feature_config, discovered_models.values())
#     )
#
#     assert (
#         len(matches) == 1
#     ), "Config object of type %s not identifiable: %i items found." % (
#         type(search_instance_type),
#         len(matches),
#     )
#
#     ret: Type[search_instance_type] = matches[0].config
#
#     assert isinstance(ret, search_instance_type), "%s is not a Config %s object." % (
#         type(ret),
#         type(search_instance_type),
#     )
#
#     return ret
