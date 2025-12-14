import pathlib
from typing import Dict, List

import pydot
from dagster import (
    AssetKey,
    AssetsDefinition,
    In,
    Out, AssetIn, OpDefinition,
)

from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__features_in
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__CONFIG
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__scrape_networks
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__compose
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__docker_compose_graph
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__cmd
from OpenStudioLandscapes.engine.base.ops.factories import factory_compose_scope__group_out
from OpenStudioLandscapes.engine.config.models import ComposeScopeBaseModel
from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE


def get_compose_scope_group__features_in(
    ASSET_HEADER: Dict,
    features: Dict,
) -> AssetsDefinition:

    dynamic_ins = {}
    dynamic_keys_by_input_name = {}

    k: str
    v: AssetIn
    for k, v in features.items():
        dynamic_ins[k] = In()  # In(<type>): type is not really relevant for now.
        dynamic_keys_by_input_name[k] = v.key

    compose_scope_op__features_in: OpDefinition = factory_compose_scope__features_in(
        name=f"op_compose_scope__features_in__{ASSET_HEADER['group_name']}",
        ins={
            "group_out_base": In(Dict),
            **dynamic_ins,
        },
        out={
            "features_in": Out(Dict),
        },
    )

    compose_scope__features_in: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__features_in,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={
            "group_out_base": AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out_base"]),
            **dynamic_keys_by_input_name,
        },
        keys_by_output_name={},
    )

    return compose_scope__features_in


def get_compose_scope_group__CONFIG(
    ASSET_HEADER: Dict,
    compose_scope: str,
) -> AssetsDefinition:

    compose_scope_op__CONFIG: OpDefinition = factory_compose_scope__CONFIG(
        name=f"op_compose_scope__CONFIG__{ASSET_HEADER['group_name']}",
        compose_scope=compose_scope,
        asset_header=ASSET_HEADER,
        ins={
            "features_in": In(Dict),
        },
        out={
            "CONFIG": Out(ComposeScopeBaseModel),
        },
    )

    compose_scope__CONFIG: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__CONFIG,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return compose_scope__CONFIG


def get_compose_scope_group__scrape_networks(
    ASSET_HEADER: Dict,
) -> AssetsDefinition:

    compose_scope_op__scrape_networks: OpDefinition = factory_compose_scope__scrape_networks(
        name=f"op_compose_scope__scrape_networks__{ASSET_HEADER['group_name']}",
        ins={
            "features_in": In(Dict),
        },
        out={
            "scrape_networks": Out(Dict),
        },
    )

    compose_scope__scrape_networks: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__scrape_networks,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return compose_scope__scrape_networks


def get_compose_scope_group__compose(
    ASSET_HEADER: Dict,
    compose_scope: str,
) -> AssetsDefinition:

    compose_scope_op__compose: OpDefinition = factory_compose_scope__compose(
        compose_scope=compose_scope,
        name=f"op_compose_scope__compose__{ASSET_HEADER['group_name']}",
        ins={
            "features_in": In(Dict),
            "scrape_networks": In(Dict),
            "CONFIG": In(ComposeScopeBaseModel),
        },
        out={
            "compose": Out(Dict),
        },
    )

    compose_scope__compose: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__compose,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return compose_scope__compose


def get_compose_scope_group__docker_compose_graph(
    ASSET_HEADER: Dict,
) -> AssetsDefinition:

    compose_scope_op__docker_compose_graph: OpDefinition = factory_compose_scope__docker_compose_graph(
        name=f"op_compose_scope__docker_compose_graph__{ASSET_HEADER['group_name']}",
        ins={
            "group_out": In(pathlib.Path),
            "compose_project_name": In(str),
        },
        out={
            "docker_compose_graph": Out(pydot.Dot),
            "docker_compose_graph_dot": Out(pathlib.Path),
        },
    )

    compose_scope__docker_compose_graph: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__docker_compose_graph,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return compose_scope__docker_compose_graph


def get_compose_scope_group__cmd(
    ASSET_HEADER: Dict,
) -> AssetsDefinition:

    compose_scope_op__cmd: OpDefinition = factory_compose_scope__cmd(
        name=f"op_compose_scope__cmd__{ASSET_HEADER['group_name']}",
        ins={},
        out={
            "cmd_append": Out(Dict),
            "cmd_extend": Out(List),
        },
    )

    compose_scope__cmd: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__cmd,
        can_subset=False,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return compose_scope__cmd


def get_compose_scope_group__group_out(
    ASSET_HEADER: dict,
    compose_scope: str,
) -> AssetsDefinition:

    compose_scope_op__group_out: OpDefinition = factory_compose_scope__group_out(
        name=f"op_compose_scope__group_out__{ASSET_HEADER['group_name']}",
        compose_scope=compose_scope,
        ins={
            "features_in": In(Dict),
            "CONFIG": In(ComposeScopeBaseModel),
            "cmd_append": In(Dict[str, List]),
            "cmd_extend": In(List),
            "compose": In(Dict),
        },
        out={
            "group_out": Out(pathlib.Path),
            "compose_project_name": Out(str),
            "docker_compose_commands": Out(Dict[str, List]),
        },
    )

    compose_scope__group_out: AssetsDefinition = AssetsDefinition.from_op(
        compose_scope_op__group_out,
        group_name=ASSET_HEADER["group_name"],
        key_prefix=ASSET_HEADER["key_prefix"],
        keys_by_input_name={},
        keys_by_output_name={},
    )

    return compose_scope__group_out


# # TEMPLATE (ASSET DEFINITION)
# def get_compose_scope_group__template(
#     ASSET_HEADER: dict,
# ) -> AssetsDefinition:
#     """
#     Usage:
#
#     ```python
#     compose_scope_asset_defs = []
#
#     # template
#     # - template_out_1
#     # - template_out_n
#     compose_scope_group__template = get_compose_scope_group__template(
#         ASSET_HEADER=ASSET_HEADER
#     )
#
#     compose_scope_asset_defs.append(compose_scope_group__template)
#     ```
#
#     Args:
#         ASSET_HEADER: dict = {
#             "group_name": str,
#             "key_prefix": list(str),
#             "compute_kind": "python",
#         }
#
#     Returns:
#         dagster.AssetsDefinition
#
#     """
#
#     compose_scope_op__template = factory_compose_scope__template(
#         name=f"op_compose_scope__template__{ASSET_HEADER['group_name']}",
#         ins={
#             # "template_in_1": In(dict),
#             # "template_in_n": In(dict),
#         },
#         out={
#             "template_out_1": Out(dict),
#             "template_out_n": Out(dict),
#         },
#     )
#
#     compose_scope__template = AssetsDefinition.from_op(
#         compose_scope_op__template,
#         # Todo:
#         #  - [ ] Change to AssetKey
#         # tags_by_output_name={
#         #     # "compose": {
#         #     #     "compose": "third_party",
#         #     # },
#         # },
#         group_name=ASSET_HEADER["group_name"],
#         key_prefix=ASSET_HEADER["key_prefix"],
#         keys_by_input_name={
#             # "template_in_1": AssetKey([*ASSET_HEADER["key_prefix"], "template_in_1"]),
#             # "template_in_n": AssetKey([*ASSET_HEADER["key_prefix"], "template_in_n"]),
#         },
#         keys_by_output_name={
#             "template_out_1": AssetKey([*ASSET_HEADER["key_prefix"], "scrape_networks"]),
#             "template_out_n": AssetKey([*ASSET_HEADER["key_prefix"], "scrape_networks"]),
#         },
#     )
#
#     return compose_scope__template
