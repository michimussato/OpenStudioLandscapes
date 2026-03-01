from typing import Dict, List

from dagster import (
    AssetsDefinition,
    OpDefinition,
    Out,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_cmd


def get_feature__cmd(
    ASSET_HEADER: Dict,
    # cmd_append: Dict[str, List],
    # cmd_extend: List,
) -> AssetsDefinition:

    cmd_op: OpDefinition = factory_cmd(
        name=f"op_feature__cmd__{ASSET_HEADER['group_name']}",
        # cmd_append=cmd_append,
        # cmd_extend=cmd_extend,
        ins={},
        out={
            "cmd_append": Out(Dict),
            "cmd_extend": Out(List),
        },
    )

    cmd: AssetsDefinition = AssetsDefinition.from_op(
        cmd_op,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return cmd
