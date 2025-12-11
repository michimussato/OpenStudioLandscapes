from importlib.metadata import Distribution
from typing import Dict

from dagster import (
AssetExecutionContext,
)

from OpenStudioLandscapes.engine.discovery import discovery


def get_feature_base_model(
        context: AssetExecutionContext,
        discovered_models: Dict[str, discovery.OpenStudioLandscapesDiscoveredFeature],
        distribution: Distribution,
) -> discovery.FeatureBaseModel:
    """
    We are not create a new Config object for this Feature. It
    was pre-made during the bootstrapping process.
    We just need to find it in the `discovery.DISCOVERED_MODELS` dict.

    Find the OpenStudioLandscapesFeature from the discovered models
    that matches the package name and return its Config object.

    Returns:
        discovery.OpenStudioLandscapesFeature

    Raises:
        ValueError
    """

    # Todo
    #  - [ ] This is a bit of a naive approach and could be done better

    for package, feature in discovered_models.items():
        # package = 'OpenStudioLandscapes-Kitsu'
        # package_discovered: str = package
        # context.log.error(f"{package_discovered = }")
        # package_discovered = 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu'
        # if package.split(".")[0] == distribution.name:
        if feature.config.distribution == distribution:
            feature_config: discovery.FeatureBaseModel = feature.config
            return feature_config
    else:
        context.log.error(f"No Config found for {distribution.name}")
        raise ValueError(f"No Config found for {distribution.name}")
