from typing import Dict

from dagster import (
    AssetKey,
    AssetSpec,
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.landscape_map.assets
from OpenStudioLandscapes.engine.compose_scopes.constants import (
    COMPOSE_SCOPE_GROUP_PREFIX,
)
from OpenStudioLandscapes.engine.constants import (
    ASSET_HEADER_BASE,
)
from OpenStudioLandscapes.engine.discovery import discovery
from OpenStudioLandscapes.engine.utils import get_dynamic_ins

assets_base = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.landscape_map.assets],
)


feature_ins = get_dynamic_ins(
    imported_features=discovery.DISCOVERED_MODELS,
)


LOGGER = discovery.LOGGER


LOGGER.info(f"{feature_ins = }")

assets_external = []


ins = {}
_compose_scopes = set()


compose_scope: str
feature: Dict[str, AssetSpec]
for compose_scope, _ in feature_ins.items():
    # get_dynamic_ins() filters for enabled Features already
    if compose_scope in _compose_scopes:
        continue
    _compose_scopes.update(compose_scope)

    ASSET_HEADER = {
        "group_name": f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
        "key_prefix": [
            "ComposeScopes",
            f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
        ],
        "compute_kind": "python",
    }

    compose_scope_asset_spec = AssetSpec(
        key=AssetKey(
            # ComposeScopes / ComposeScope_DEV_default / docker_compose_graph_dot
            [
                *ASSET_HEADER["key_prefix"],
                "docker_compose_graph_dot",
            ]
        ),
        group_name=ASSET_HEADER["group_name"],
        description="Todo",
    )
    ins[f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}"] = compose_scope_asset_spec

    assets_external.append(compose_scope_asset_spec)


# for testing:
# if assets_external is empty at this point,
# just add a dummy to match the dummy AssetIn
# defined in the assets.py (if not bool(ins))
# so that we have a visual representation of
# the dependencies
if not bool(assets_external):
    compose_scope = "dummy_compose_scope"
    asset_spec = AssetSpec(
        key=AssetKey(
            # ComposeScopes / dummy_compose_scope / docker_compose_graph_dot
            [
                "ComposeScopes",
                f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
                "docker_compose_graph_dot",
            ]
        ),
        group_name=f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
        description="Todo",
    )
    assets_external.append(asset_spec)


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

# assets_external is meant for the Definitions object in
# _definitions_with_upstream_specs.py for now.
assets_external.append(group_out_base)


defs = Definitions(
    assets=[
        *assets_base,
    ],
)
