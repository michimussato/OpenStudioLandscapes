import os
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
from OpenStudioLandscapes.engine.enums import *


@asset(
    **ASSET_HEADER_COMPOSE_LICENSE_SERVER,
    ins={
        "group_in": AssetIn(AssetKey([*KEY_BASE, "group_out"])),
    },
    deps=[
        AssetKey(
            [
                *ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"],
                f"constants_{ASSET_HEADER_COMPOSE_LICENSE_SERVER['group_name']}",
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
            "COMPOSE_SCOPE": ComposeScope.LICENSE_SERVER,
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
    if compose_scope == ComposeScope.LICENSE_SERVER:
        split = module.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))


@asset(
    **ASSET_HEADER_COMPOSE_LICENSE_SERVER,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_COMPOSE_LICENSE_SERVER, "env"]),
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
        f"{GROUP_COMPOSE_LICENSE_SERVER}__{'__'.join(KEY_COMPOSE_LICENSE_SERVER)}",
        "__".join(context.asset_key.path),
        "docker_compose",
        "docker-compose.yml",
    )

    context.log.info(docker_compose)
    context.log.info(type(docker_compose))

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


group_out = AssetsDefinition.from_op(
    op_group_out,
    can_subset=True,
    group_name=GROUP_COMPOSE_LICENSE_SERVER,
    key_prefix=KEY_COMPOSE_LICENSE_SERVER,
    keys_by_input_name={
        "compose": AssetKey([*KEY_COMPOSE_LICENSE_SERVER, "compose"]),
        "env": AssetKey([*KEY_COMPOSE_LICENSE_SERVER, "env"]),
        "group_in": AssetKey([*KEY_BASE, "group_out"]),
    },
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=GROUP_COMPOSE_LICENSE_SERVER,
    key_prefix=KEY_COMPOSE_LICENSE_SERVER,
    keys_by_input_name={
        "group_out": AssetKey([*KEY_COMPOSE_LICENSE_SERVER, "group_out"]),
        "compose_project_name": AssetKey([*KEY_COMPOSE_LICENSE_SERVER, "compose_project_name"]),
    },
)
