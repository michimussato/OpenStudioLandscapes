from typing import Dict

from dagster import (
    AssetIn,
    AssetKey,
    AssetSpec,
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose_scopes.assets
from OpenStudioLandscapes.engine.compose_scopes import GRAFANA_AVAILABLE
from OpenStudioLandscapes.engine.constants import (
    ASSET_HEADER_BASE,
)

assets_base = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.compose_scopes.assets]
)

from OpenStudioLandscapes.engine.compose_scopes.resources import configurable_resources_base

from OpenStudioLandscapes.engine.compose_scopes.assets import DYNAMIC_INS
from OpenStudioLandscapes.engine.compose_scopes.constants import (
    COMPOSE_SCOPE_GROUP_PREFIX,
)
from OpenStudioLandscapes.engine.discovery import discovery

LOGGER = discovery.LOGGER


LOGGER.debug(f"{DYNAMIC_INS = }")
# {'default': {'OpenStudioLandscapes_filebrowser': AssetIn(key=AssetKey(['OpenStudioLandscapes_filebrowser', 'feature_out_v2']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}}

assets_external = []


if bool(DYNAMIC_INS):

    compose_scope: str
    feature: Dict[str, discovery.OpenStudioLandscapesDiscoveredFeature]
    LOGGER.debug(f"{DYNAMIC_INS = }")
    for compose_scope, features in DYNAMIC_INS.items():
        LOGGER.debug(f"{features = }")
        # features = {'OpenStudioLandscapes_filebrowser': AssetIn(key=AssetKey(['OpenStudioLandscapes_filebrowser', 'feature_out_v2']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}

        feature_name: str
        asset_in: AssetIn
        for feature_name, asset_in in features.items():
            asset_key: AssetKey = asset_in.key

            LOGGER.debug(f"{asset_key = }")

            asset_spec = AssetSpec(
                asset_key,  # contains key, key_prefix, group
                description="Todo",
                group_name="Features",  # Don't know how to retrieve the "group_name" from an AssetKey
            )

            assets_external.append(asset_spec)

        if GRAFANA_AVAILABLE:
            from OpenStudioLandscapes.Grafana import (
                ASSET_HEADER as ASSET_HEADER_GRAFANA,
            )

            for asset_spec in [
                "build_docker_image_alloy",
                "alloy_config",
            ]:
                asset_spec_alloy = AssetSpec(
                    key=AssetKey(
                        [
                            *ASSET_HEADER_GRAFANA["key_prefix"],
                            asset_spec,
                        ]
                    ),
                    group_name=ASSET_HEADER_GRAFANA["group_name"],
                    description="`AssetSpec` for `AssetDefinition` specified in "
                    "`OpenStudioLandscapes.engine.base.assets.group_out_base`.",
                )
                assets_external.append(asset_spec_alloy)


# for testing:
# if assets_external is empty at this point,
# just add a dummy to match the dummy AssetIn
# defined in the assets.py (if not bool(ins))
# so that we have a visual representation of
# the dependencies
if not bool(assets_external) and not bool(DYNAMIC_INS):
    compose_scope = "dummy_feature"
    feature_out = AssetSpec(
        key=AssetKey(
            [
                "OpenStudioLandscapes_dummy",
                "feature_out_v2",
            ]
        ),
        group_name=f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
        description="Todo",
    )
    assets_external.append(feature_out)


group_out_base = AssetSpec(
    key=AssetKey(
        [
            *ASSET_HEADER_BASE["key_prefix"],
            "group_out_base",
        ]
    ),
    group_name=ASSET_HEADER_BASE["group_name"],
    description="`AssetSpec` for `AssetDefinition` specified in "
    "`OpenStudioLandscapes.engine.base.assets.group_out_base`.",
)

assets_external.append(group_out_base)


defs = Definitions(
    assets=[
        *assets_base,
        # *constants,
        # *assets_external,
    ],
    resources={
        **configurable_resources_base,
    },
)
