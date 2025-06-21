from dagster import (
    In,
    Out,
    AssetsDefinition,
    AssetKey,
)

from OpenStudioLandscapes.engine.base.ops import factory_group_in


# get_base_in ?
def get_group_in(
        ASSET_HEADER: dict,
        ASSET_HEADER_PARENT: dict,
        # Todo:
        #  - [ ] To accept an input_name here is not very elegant
        input_name: str = "group_out",
) -> AssetsDefinition:

    group_in_op = factory_group_in(
        name=f"op_group_in_{ASSET_HEADER['group_name']}",
        ins={
            input_name: In(dict),
        },
        out={
            "group_in": Out(dict),
        },
    )

    group_in = AssetsDefinition.from_op(
        group_in_op,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        # key_prefix=ASSET_HEADER["key_prefix"]: This can be deceiving: Prefixes everything on top of all
        # other Prefixes
        keys_by_input_name={
            input_name: AssetKey([*ASSET_HEADER_PARENT["key_prefix"], input_name]),
        },
        keys_by_output_name={
            "group_in": AssetKey([*ASSET_HEADER["key_prefix"], "group_in"]),
        },
    )

    return group_in
