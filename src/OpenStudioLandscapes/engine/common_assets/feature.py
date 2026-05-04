from typing import Dict, Type

from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    OpDefinition,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory__CONFIG
from OpenStudioLandscapes.engine.discovery import discovery
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesFeatureIn


def get_feature__CONFIG(
    ASSET_HEADER: Dict,
    CONFIG_STR: str,
    search_model_of_type: Type[discovery.FeatureBaseModel],
) -> AssetsDefinition:

    feature_in_op__CONFIG: OpDefinition = factory__CONFIG(
        name=f"op__CONFIG__{ASSET_HEADER['group_name']}",
        CONFIG_STR=CONFIG_STR,
        search_model_of_type=search_model_of_type,
        ins={
            "feature_in": In(OpenStudioLandscapesFeatureIn),
        },
        out={
            "CONFIG": Out(discovery.FeatureBaseModel),
            # Todo:
            #  - [ ] Can we do this dynamically based on whether there is a parent?
            # "CONFIG_PARENT": Out(discovery.FeatureBaseModel),
        },
    )

    feature_in__CONFIG: AssetsDefinition = AssetsDefinition.from_op(
        feature_in_op__CONFIG,
        # Experimental Feature:
        # key_prefix=ASSET_HEADER["key_prefix"],
        group_name=ASSET_HEADER["group_name"],
        keys_by_input_name={
            # Without these:
            # [2026-04-30 20:48:30] WARNING:dagster:/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/definitions/resolved_asset_deps.py:24: ExperimentalWarning: Asset ["OpenStudioLandscapes_Flamenco_Worker", "CONFIG"]'s dependency 'feature_in' was resolved to upstream asset ["OpenStudioLandscapes_Flamenco_Worker", "feature_in"], because the name matches and they're in the same group. This is experimental functionality that may change in a future release is experimental. It may break in future versions, even between dot releases. To mute warnings for experimental functionality, invoke warnings.filterwarnings("ignore", category=dagster.ExperimentalWarning) or use one of the other methods described at https://docs.python.org/3/library/warnings.html#describing-warning-filters.
            #   self._deps_by_assets_def_id = resolve_assets_def_deps(assets_defs, source_assets)
            "feature_in": AssetKey([*ASSET_HEADER["key_prefix"], "feature_in"]),
        },
        keys_by_output_name={
            "CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
        },
    )

    return feature_in__CONFIG
