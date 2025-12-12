from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope
from OpenStudioLandscapes.engine.config.models import FeatureBaseModel


def get_compose_scope_group(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    compose_scope_op = factory_compose_scope(
        name=f"op_compose_scope_group_{ASSET_HEADER['group_name']}",
        ins={
            # "compose_networks": In(dict),
            # "compose_maps": In(list),
            # "CONFIG": In(FeatureBaseModel),
            # # "group_in": In(dict)
        },
        out={
            "test_output_1": Out(dict),
            "test_output_2": Out(dict),
        },
    )

    compose_scope = AssetsDefinition.from_op(
        compose_scope_op,
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
