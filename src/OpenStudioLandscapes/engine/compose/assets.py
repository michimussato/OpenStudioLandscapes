import os
import copy
import pathlib
from typing import Generator, MutableMapping, Any

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
    multi_asset,
    AssetOut,
)

from OpenStudioLandscapes.engine.base.ops import (
    op_docker_compose_graph,
    # op_group_in,
    op_group_out,
)
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *


# @multi_asset(
#     name=f"constants_{GROUP_COMPOSE}",
#     ins={
#         "features_in": AssetIn(
#             AssetKey([*KEY_COMPOSE, "features_in"])
#         )
#     },
#     outs={
#         "ENV_TEST": AssetOut(
#             **ASSET_HEADER_COMPOSE,
#             dagster_type=str,
#             description="",
#         ),
#         "FEATURE_CONFIGS": AssetOut(
#             **ASSET_HEADER_COMPOSE,
#             dagster_type=dict,
#             description="",
#         ),
#     },
# )
# def constants_multi_asset(
#     context: AssetExecutionContext,
#     features_in: dict,
# ) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
#     """ """
#
#     yield Output(
#         output_name="FEATURE_CONFIGS",
#         value=FEATURE_CONFIGS,
#     )
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key_for_output("FEATURE_CONFIGS"),
#         metadata={
#             "__".join(
#                 context.asset_key_for_output("FEATURE_CONFIGS").path
#             ): MetadataValue.json(FEATURE_CONFIGS),
#         },
#     )
#
#     yield Output(
#         output_name="NAME",
#         value=__name__,
#     )
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key_for_output("NAME"),
#         metadata={
#             "__".join(context.asset_key_for_output("NAME").path): MetadataValue.path(
#                 __name__
#             ),
#         },
#     )


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "group_in": AssetIn(AssetKey([*KEY_BASE, "group_out"])),
        "constants_compose": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "constants_compose"])),
        "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "features_in"])),
    },
    # deps=[
    #     AssetKey(
    #         [*ASSET_HEADER_COMPOSE['key_prefix'], "constants_compose"]
    #     )
    # ],
)
def env(
    context: AssetExecutionContext,
    group_in: dict,
    constants_compose: dict,
    features_in: dict,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    ret = group_in.get("env", {})

    ret.update(
        {
            "COMPOSE_SCOPE": ComposeScope.DEFAULT,
        }
    )

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "features_in"])),
    },
    # deps=[
    #     AssetKey(
    #         [*ASSET_HEADER_COMPOSE['key_prefix'], "constants_compose"]
    #     )
    # ],
)
def env_base(
    context: AssetExecutionContext,
    features_in: dict,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    context.log.info(features_in)

    _env_base = features_in.pop("env_base", {})

    yield Output(_env_base)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_env_base),
        },
    )


# Dynamic inputs based on the imported
# third party code locations
ins = {}
feature_ins = {}
for i in IMPORTED_FEATURES:
    # ex: module = "OpenStudioLandscapes.Ayon.definitions"
    module = i["module"]
    compose_scope = i["compose_scope"]
    if compose_scope == ComposeScope.DEFAULT:
        split = module.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))
        # feature_ins[f"{split[0]}_{split[1]}"] = AssetKey([key, "feature_out"])
        feature_ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "feature_out"]))
        # feature_ins[f"{split[0]}_{split[1]}"].pop("env_base")



@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_COMPOSE, "env"]),
        ),
        **ins,
    },
)
def compose(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    **kwargs,
) -> Generator[
    Output[dict[str, list[dict[str, list]]]] | AssetMaterialization, None, None
]:
    """ """

    context.log.info(kwargs)

    _group_in = []

    docker_compose = pathlib.PurePosixPath(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{GROUP_COMPOSE_WORKER}__{'__'.join(KEY_COMPOSE_WORKER)}",
        "__".join(context.asset_key.path),
        "docker_compose",
        "docker-compose.yml",
    )

    for v in kwargs.values():
        _rel_path = os.path.relpath(
            path=v.as_posix(),
            start=docker_compose.parent.as_posix(),
        )
        rel_path = pathlib.Path(_rel_path)

        _group_in.append(rel_path)

    docker_dict = {
        "include": [{"path": [i.as_posix()]} for i in _group_in],
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_COMPOSE, "env"]),
        ),
        "features_in": AssetIn(
            AssetKey([*KEY_COMPOSE, "features_in"]),
        ),
        # **ins,
    },
)
def compose_feature(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    features_in: dict,  # pylint: disable=redefined-outer-name
    # **kwargs,
) -> Generator[
    Output[dict[str, list[dict[str, list]]]] | AssetMaterialization, None, None
]:
    """ """

    context.log.info(features_in)

    _group_in = []

    docker_compose = pathlib.PurePosixPath(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{GROUP_COMPOSE_WORKER}__{'__'.join(KEY_COMPOSE_WORKER)}",
        "__".join(context.asset_key.path),
        "docker_compose",
        "docker-compose.yml",
    )

    # env_base = features_in.pop("env_base", {})
    # constants_base = features_in.pop("constants_base", {})

    for k in features_in.keys():
        v = features_in[k].get("compose", {})

        context.log.info(v)

    context.log.info(features_in)

    docker_dict = {
        "include": [{"path": [i.as_posix()]} for i in _group_in],
        # "include": [{"path": [i]} for i in _group_in],
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "group_out_base": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out"])),
        **feature_ins,
    },
)
def features_in(
    context: AssetExecutionContext,
    group_out_base: dict,  # pylint: disable=redefined-outer-name
    # env: dict,  # pylint: disable=redefined-outer-name
    **kwargs,
) -> Generator[
    Output[dict[str, list[dict[str, list]]]] | AssetMaterialization, None, None
]:
    """ """

    context.log.info(kwargs)

    env_base = group_out_base["env_base"]

    # docker_compose_yaml: dict[str, pathlib.Path] = {}
    docker_compose_yaml: dict[str, str] = {}
    docker_compose: dict[str, Any] = {}

    for k, v in kwargs.items():
        # remove
        # - env_base
        # - constants_base
        # - features
        # from kwargs dicts
        for d in [
            "env_base",
            "constants_base",
            "features"
        ]:
            kwargs[k].pop(d)

        docker_compose_yaml[k] = str(kwargs[k]["compose_yaml"])
        docker_compose[k] = str(kwargs[k]["compose"])

    kwargs["env_base"] = env_base

    metadata = {}

    out_ = copy.deepcopy(kwargs)

    # JSON cannot serialize certain types
    # out of the box. This makes sure that
    # MetadataValue.json receives only
    # serializable input.
    def _serialize(d):
        for k_, v_ in d.items():
            if isinstance(v_, dict):
                _serialize(v_)
            elif isinstance(v_, pathlib.PosixPath):
                d[k_] = v_.as_posix()
            else:
                d[k_] = str(v_)

    _serialize(out_)

    for k, v in out_.items():
        context.log.warning(k)
        context.log.warning(v)
        metadata[k] = MetadataValue.json(v)

    yield Output(kwargs)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(out_),
            "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
            "docker_compose": MetadataValue.json(docker_compose),
            **metadata,
        },
    )


# group_in = AssetsDefinition.from_op(
#     op_group_in,
#     can_subset=False,
#     group_name=ASSET_HEADER_COMPOSE["group_name"],
#     # This can be deceiving: Prefixes everything on top of all
#     # other Prefixes
#     # key_prefix=ASSET_HEADER["key_prefix"],
#     keys_by_input_name=feature_ins,
#     # keys_by_input_name={
#     #     "group_out": AssetKey([*KEY_BASE, "group_out"]),
#     # },
#     keys_by_output_name={
#         "group_in": AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "group_in"]),
#     },
# )


group_out = AssetsDefinition.from_op(
    op_group_out,
    can_subset=True,
    group_name=GROUP_COMPOSE,
    key_prefix=KEY_COMPOSE,
    keys_by_input_name={
        "compose": AssetKey([*KEY_COMPOSE, "compose"]),
        "env": AssetKey([*KEY_COMPOSE, "env"]),
        "group_in": AssetKey([*KEY_BASE, "group_out"]),
    },
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=GROUP_COMPOSE,
    key_prefix=KEY_COMPOSE,
    keys_by_input_name={
        "group_out": AssetKey([*KEY_COMPOSE, "group_out"]),
        "compose_project_name": AssetKey([*KEY_COMPOSE, "compose_project_name"]),
    },
)
