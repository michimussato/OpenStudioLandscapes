from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_scrape_networks


def get_scrape_networks(
    ASSET_HEADER: dict,
) -> AssetsDefinition:

    scrape_networks_op = factory_scrape_networks(
        name=f"op_docker_config_{ASSET_HEADER['group_name']}",
        ins={
            "features_in": In(dict),
        },
        out={
            "scrape_networks": Out(dict),
        },
    )

    scrape_networks = AssetsDefinition.from_op(
        scrape_networks_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        keys_by_output_name={
            "scrape_networks": AssetKey([*ASSET_HEADER["key_prefix"], "scrape_networks"]),
        },
        keys_by_input_name={
            "features_in": AssetKey([*ASSET_HEADER["key_prefix"], "features_in"]),
        },
    )

    return scrape_networks
