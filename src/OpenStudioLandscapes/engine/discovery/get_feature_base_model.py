from typing import Dict, Type

from dagster import (
    AssetExecutionContext,
)

from OpenStudioLandscapes.engine.discovery import discovery


def get_feature_base_model(
    context: AssetExecutionContext,
    discovered_models: Dict[str, discovery.OpenStudioLandscapesDiscoveredFeature],
    search_instance_type: Type[discovery.FeatureBaseModel,],
) -> discovery.FeatureBaseModel:
    """
    We are not create a new Config object for this Feature. It
    was pre-made during the bootstrapping process.
    We just need to find it in the `discovery.DISCOVERED_MODELS` dict.

    Find the OpenStudioLandscapesFeature from the discovered models
    that matches the package name and return its Config object.

    As all Feature Config objects are subclasses of
    discovery.OpenStudioLandscapesFeature and also singletons,
    there will always only be one Config object of type
    <search_instance_type>.

    Returns:
        Subclass of discovery.OpenStudioLandscapesFeature

    Raises:
        ValueError
    """

    for package, feature in discovered_models.items():
        feature_config: discovery.FeatureBaseModel = feature.config
        if isinstance(feature_config, search_instance_type):
            return feature_config
    else:
        msg = f"No Config object of type {type(search_instance_type)} found."
        context.log.error(msg)
        raise ValueError(msg)
