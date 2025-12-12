from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope_test
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__features_in
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__CONFIG
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel


def get_compose_scope_group_test(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    compose_scope_op_test = factory_compose_scope_test(
        name=f"op_compose_scope_group_{ASSET_HEADER['group_name']}",
        ins={
            # "compose_networks": In(dict),
            # "compose_maps": In(list),
            # "CONFIG": In(FeatureBaseModel),
            # # "group_in": In(dict)
        },
        out={
            "multi_asset__test_output_1": Out(dict),
            "multi_asset__test_output_2": Out(dict),
        },
    )

    compose_scope = AssetsDefinition.from_op(
        compose_scope_op_test,
        # Todo:
        #  - [ ] Change to AssetKey
        # tags_by_output_name={
        #     # "compose": {
        #     #     "compose": "third_party",
        #     # },
        # },
        keys_by_output_name={
            # "scrape_networks": AssetKey(
            #     [*ASSET_HEADER["key_prefix"], "scrape_networks"]
            # ),
        },
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={
            # "compose_networks": AssetKey(
            #     [*ASSET_HEADER["key_prefix"], "compose_networks"]
            # ),
            # "compose_maps": AssetKey([*ASSET_HEADER["key_prefix"], "compose_maps"]),
            # "CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
            # # "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
        # keys_by_input_name={
        #     "features_in": AssetKey([*ASSET_HEADER["key_prefix"], "features_in"]),
        # },
    )

    return compose_scope


def get_compose_scope_group__features_in(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    compose_scope_op__features_in = factory_compose_scope__features_in(
        name=f"op_compose_scope__features_in__{ASSET_HEADER['group_name']}",
        ins={
            # "compose_networks": In(dict),
            # "compose_maps": In(list),
            # "CONFIG": In(FeatureBaseModel),
            # # "group_in": In(dict)
        },
        out={
            "features_in": Out(dict),
            # "test_output_2": Out(dict),
        },
    )

    compose_scope__features_in = AssetsDefinition.from_op(
        compose_scope_op__features_in,
        # Todo:
        #  - [ ] Change to AssetKey
        # tags_by_output_name={
        #     # "compose": {
        #     #     "compose": "third_party",
        #     # },
        # },
        keys_by_output_name={
            # "scrape_networks": AssetKey(
            #     [*ASSET_HEADER["key_prefix"], "scrape_networks"]
            # ),
        },
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={
            # "compose_networks": AssetKey(
            #     [*ASSET_HEADER["key_prefix"], "compose_networks"]
            # ),
            # "compose_maps": AssetKey([*ASSET_HEADER["key_prefix"], "compose_maps"]),
            # "CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
            # # "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
        # keys_by_input_name={
        #     "features_in": AssetKey([*ASSET_HEADER["key_prefix"], "features_in"]),
        # },
    )

    return compose_scope__features_in


def get_compose_scope_group__CONFIG(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    compose_scope_op__CONFIG = factory_compose_scope__CONFIG(
        name=f"op_compose_scope__CONFIG__{ASSET_HEADER['group_name']}",
        ins={
            # "compose_networks": In(dict),
            # "compose_maps": In(list),
            # "CONFIG": In(FeatureBaseModel),
            # # "group_in": In(dict)
        },
        out={
            "CONFIG": Out(dict),
            # "test_output_2": Out(dict),
        },
    )

    compose_scope__CONFIG = AssetsDefinition.from_op(
        compose_scope_op__CONFIG,
        # Todo:
        #  - [ ] Change to AssetKey
        # tags_by_output_name={
        #     # "compose": {
        #     #     "compose": "third_party",
        #     # },
        # },
        keys_by_output_name={
            # "scrape_networks": AssetKey(
            #     [*ASSET_HEADER["key_prefix"], "scrape_networks"]
            # ),
        },
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={
            # "compose_networks": AssetKey(
            #     [*ASSET_HEADER["key_prefix"], "compose_networks"]
            # ),
            # "compose_maps": AssetKey([*ASSET_HEADER["key_prefix"], "compose_maps"]),
            # "CONFIG": AssetKey([*ASSET_HEADER["key_prefix"], "CONFIG"]),
            # # "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
        # keys_by_input_name={
        #     "features_in": AssetKey([*ASSET_HEADER["key_prefix"], "features_in"]),
        # },
    )

    return compose_scope__CONFIG
