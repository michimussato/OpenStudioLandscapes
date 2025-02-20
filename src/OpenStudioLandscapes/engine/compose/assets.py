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

from OpenStudioLandscapes.engine.base.assets import KEY as KEY_BASE
from OpenStudioLandscapes.engine.base.ops import op_docker_compose_graph, op_group_out
from OpenStudioLandscapes.engine.constants import THIRD_PARTY

GROUP = "Compose"
KEY = "Compose"

asset_header = {
    "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python",
}


@asset(
    **asset_header,
    ins={
        "group_in": AssetIn(AssetKey([KEY_BASE, "group_out"])),
    },
)
def env(
    context: AssetExecutionContext,
    group_in: dict,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    ret = group_in.get("env", {})

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
    try:
        # ex: i = "OpenStudioLandscapes_Ayon.definitions"
        s = i.split(".", maxsplit=1)[0]  # s = "OpenStudioLandscapes_Ayon"
        key = s.split("_", maxsplit=1)[1]  # key = "Ayon"
        ins[s] = AssetIn(AssetKey([key, "group_out"]))
    except IndexError:
        # ex: i = "OpenStudioLandscapes.Ayon.definitions"
        split = i.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))


@asset(
    **asset_header,
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

    _group_in = [*kwargs.values()]

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
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "compose": AssetKey([KEY, "compose"]),
        "env": AssetKey([KEY, "env"]),
    },
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "group_out": AssetKey([KEY, "group_out"]),
    },
)
