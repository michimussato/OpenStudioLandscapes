import pathlib
from typing import Generator

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
)

from OpenStudioLandscapes.engine.base.ops import op_docker_compose_graph, op_group_out
from OpenStudioLandscapes.engine.constants import *


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "group_in": AssetIn(AssetKey([*KEY_BASE, "group_out"])),
    },
    deps=[
        AssetKey(
            [
                *ASSET_HEADER_COMPOSE["key_prefix"],
                f"constants_{ASSET_HEADER_COMPOSE['group_name']}",
            ]
        )
    ],
)
def env(
    context: AssetExecutionContext,
    group_in: dict,
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


# Dynamic inputs based on the imported
# third party code locations
ins = {}
for i in THIRD_PARTY:
    enabled = i["enabled"]
    if not enabled:
        continue
    # ex: module = "OpenStudioLandscapes.Ayon.definitions"
    module = i["module"]
    compose_scope = i["compose_scope"]
    if compose_scope == ComposeScope.DEFAULT:
        split = module.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        **ins,
    },
)
def compose(
    context: AssetExecutionContext,
    **kwargs,
) -> Generator[
    Output[dict[str, list[dict[str, list]]]] | AssetMaterialization, None, None
]:
    """ """

    context.log.info(kwargs)

    _group_in = []

    for v in kwargs.values():
        # Filter None from Dummy Out
        if isinstance(v, pathlib.Path):
            _group_in.append(v)

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


group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP_COMPOSE,
    key_prefix=KEY_COMPOSE,
    keys_by_input_name={
        "compose": AssetKey([*KEY_COMPOSE, "compose"]),
        "env": AssetKey([*KEY_COMPOSE, "env"]),
    },
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=GROUP_COMPOSE,
    key_prefix=KEY_COMPOSE,
    keys_by_input_name={
        "group_out": AssetKey([*KEY_COMPOSE, "group_out"]),
    },
)
