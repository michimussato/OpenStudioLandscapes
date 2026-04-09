import enum
from typing import Dict

import yaml
from dagster import (
    AssetIn,
    AssetKey,
    get_dagster_logger,
)

LOGGER = get_dagster_logger(__name__)

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine.common_assets.compose_scope import (
    get_compose_scope_group__cmd,
    get_compose_scope_group__compose,
    get_compose_scope_group__CONFIG,
    get_compose_scope_group__docker_compose_graph,
    get_compose_scope_group__features_in,
    get_compose_scope_group__group_out,
    get_compose_scope_group__scrape_networks,
)
from OpenStudioLandscapes.engine.compose_scopes import GRAFANA_AVAILABLE
from OpenStudioLandscapes.engine.compose_scopes.constants import *
from OpenStudioLandscapes.engine.compose_scopes.simple_factories import (
    simple_factory_alloy,
    simple_factory_newt,
)
from OpenStudioLandscapes.engine.utils import *

# Todo:
#  - [ ] get assets from common_assets


# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    enum.Enum,
    yaml.representer.SafeRepresenter.represent_str,
)

feature_ins = get_dynamic_ins(
    imported_features=discovery.DISCOVERED_MODELS,
)

LOGGER.info(f"{feature_ins = }")
# feature_ins = {'default': {'OpenStudioLandscapes_Kitsu': AssetIn(key=AssetKey(['Kitsu', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_Watchtower': AssetIn(key=AssetKey(['Watchtower', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_VERT': AssetIn(key=AssetKey(['VERT', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}}

compose_scope_asset_defs = []

compose_scopes = set(feature_ins.keys())



# for testing:
# if assets_external is empty at this point,
# just add a dummy
if not bool(feature_ins):
    feature_ins =  {
        "dummy_compose_scope": {
            "OpenStudioLandscapes_dummy": AssetIn(
                key=AssetKey(
                    [
                        "OpenStudioLandscapes_dummy",
                        "feature_out_v2",
                    ]
                ),
            )
        }
    }


compose_scope: str
feature: Dict[str, discovery.OpenStudioLandscapesDiscoveredFeature]
for compose_scope, features in feature_ins.items():
    # Todo
    #  - [ ] This most likely needs a factory

    LOGGER.info(f"{features = }")
    # features = {'OpenStudioLandscapes_Kitsu': AssetIn(key=AssetKey(['OpenStudioLandscapes_Kitsu', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_Watchtower': AssetIn(key=AssetKey(['OpenStudioLandscapes_Watchtower', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)

    ASSET_HEADER = {
        "group_name": f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
        "key_prefix": [
            "ComposeScopes",
            f"{COMPOSE_SCOPE_GROUP_PREFIX}_{compose_scope}",
        ],
        "compute_kind": "python",
    }

    # features_in
    compose_scope_group__features_in = get_compose_scope_group__features_in(
        ASSET_HEADER=ASSET_HEADER,
        features=features,
    )

    compose_scope_asset_defs.append(compose_scope_group__features_in)

    # CONFIG
    compose_scope_group__CONFIG = get_compose_scope_group__CONFIG(
        ASSET_HEADER=ASSET_HEADER,
        compose_scope=compose_scope,
    )

    compose_scope_asset_defs.append(compose_scope_group__CONFIG)

    # scrape_networks
    compose_scope_group_scrape__networks = get_compose_scope_group__scrape_networks(
        ASSET_HEADER=ASSET_HEADER,
    )

    compose_scope_asset_defs.append(compose_scope_group_scrape__networks)

    # compose
    compose_scope_group__compose = get_compose_scope_group__compose(
        ASSET_HEADER=ASSET_HEADER,
        compose_scope=compose_scope,
    )

    compose_scope_asset_defs.append(compose_scope_group__compose)

    # docker_compose_graph
    # - docker_compose_graph
    # - docker_compose_graph_dot
    compose_scope_group__docker_compose_graph = (
        get_compose_scope_group__docker_compose_graph(
            ASSET_HEADER=ASSET_HEADER,
        )
    )

    compose_scope_asset_defs.append(compose_scope_group__docker_compose_graph)

    # cmd
    # - cmd_append
    # - cmd_extend
    compose_scope_group__cmd = get_compose_scope_group__cmd(
        ASSET_HEADER=ASSET_HEADER,
    )

    compose_scope_asset_defs.append(compose_scope_group__cmd)

    # group_out
    # - group_out
    # - compose_project_name
    # - docker_compose_commands
    #   -  scp -r /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-12-14-12-40-00-ef08f0b2149249128904260982ce5507/dist user@192.168.178.10:/home/user/git/repos/server/openstudiolandscapes/demo
    # - systemd_unit
    compose_scope_group__group_out = get_compose_scope_group__group_out(
        ASSET_HEADER=ASSET_HEADER,
        compose_scope=compose_scope,
    )

    compose_scope_asset_defs.append(compose_scope_group__group_out)

    # Todo
    #  - [ ] find a more programmatic implementation
    #        - use specs

    # spec = {}
    wrapper_newt = simple_factory_newt(
        ASSET_HEADER=ASSET_HEADER,
        compose_scope=compose_scope,
        name="wrapper_newt",
        ins={
            "CONFIG": AssetIn(AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"])),
            "scrape_networks": AssetIn(
                AssetKey([*ASSET_HEADER["key_prefix"], "scrape_networks"])
            ),
        },
    )
    compose_scope_asset_defs.append(wrapper_newt)

    # spec = {}
    if GRAFANA_AVAILABLE:
        wrapper_alloy = simple_factory_alloy(
            ASSET_HEADER=ASSET_HEADER,
            compose_scope=compose_scope,
            port_range_pool=compose_scopes,
            name="wrapper_alloy",
            ins={
                "CONFIG": AssetIn(
                    AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"])
                ),
                "scrape_networks": AssetIn(
                    AssetKey([*ASSET_HEADER["key_prefix"], "scrape_networks"])
                ),
                "alloy_config": AssetIn(
                    AssetKey(["OpenStudioLandscapes_Grafana", "alloy_config"])
                ),
                "build_docker_image_alloy": AssetIn(
                    AssetKey(
                        ["OpenStudioLandscapes_Grafana", "build_docker_image_alloy"]
                    )
                ),
            },
        )
        compose_scope_asset_defs.append(wrapper_alloy)
    else:
        LOGGER.critical(
            f"Alloy wrapper is not available in Compose Scopes. "
            f"Install `OpenStudioLandscapes-Grafana` Feature "
            f"to unlock this functionality."
        )
