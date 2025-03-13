import os
import base64
import pathlib
from typing import Generator

import yaml
import pydot

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
    **ASSET_HEADER_WORLD_MAP,
    ins={
        "docker_compose_graph_default": AssetIn(AssetKey(["Compose_default", "docker_compose_graph"])),
        "docker_compose_graph_worker": AssetIn(AssetKey(["Compose_worker", "docker_compose_graph"])),
    },
    # deps=[
    #     AssetKey(
    #         [
    #             *ASSET_HEADER_COMPOSE["key_prefix"],
    #             f"constants_{ASSET_HEADER_COMPOSE['group_name']}",
    #         ]
    #     )
    # ],
)
def world_map(
    context: AssetExecutionContext,
    docker_compose_graph_default: pydot.Dot,  # pylint: disable=redefined-outer-name
    docker_compose_graph_worker: pydot.Dot,  # pylint: disable=redefined-outer-name
    # group_in: dict,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    # ret = group_in.get("env", {})

    # graph = pydot.Dot(
    #     graph_name="world_graph",
    #     label="world_graph",
    #     rankdir="LR",
    #     graph_type="digraph",
    #     bgcolor="#2f2f2f",
    #     splines="line",
    #     # splines=False,
    #     pad="1.5", nodesep="0.3", ranksep="10",
    #     # **self.global_dot_settings,
    # )

    # https://stackoverflow.com/questions/16488216/graph-of-graphs-in-graphviz
    # gvpack /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_default__Compose_default/Compose_default__group_out/docker_compose/Compose_default__docker_compose_graph/Compose_default__docker_compose_graph.dot /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_worker__Compose_worker/Compose_worker__group_out/docker_compose/Compose_worker__docker_compose_graph/Compose_worker__docker_compose_graph.dot -o /home/michael/git/repos/OpenStudioLandscapes/merge_gvpack.dot
    # gvpack /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_default__Compose_default/Compose_default__group_out/docker_compose/Compose_default__docker_compose_graph/Compose_default__docker_compose_graph.dot /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-03-13_10-49-08__6b6ac8f78f874ecba37660cf1b084036/Compose_worker__Compose_worker/Compose_worker__group_out/docker_compose/Compose_worker__docker_compose_graph/Compose_worker__docker_compose_graph.dot | sed 's/_gv[0-9]\+//g' > /home/michael/git/repos/OpenStudioLandscapes/merge_dotpack.dot

    merged = pathlib.Path("/home/michael/git/repos/OpenStudioLandscapes/merge_dotpack.dot")

    graph = pydot.graph_from_dot_file(path=merged)[0]

    # graph.rankdir = "LR"
    # graph.bgcolor = "#2f2f2f"
    # graph.splines="line"
    # graph.pad="1.5"
    # graph.nodesep="0.3"
    # graph.ranksep="10"
    #
    # graph.fontname = "Helvetica"
    # graph.style = "rounded"

    docker_compose_dir = merged.parent / "__".join(context.asset_key.path)

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    # SVG
    svg = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.svg"
    graph.write(
        path=svg,
        format="svg",
    )

    with open(svg, "rb") as fr:
        svg_bytes = fr.read()

    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
    svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"

    # PNG
    png = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.png"
    graph.write(
        path=png,
        format="png",
    )

    # SLOW
    # with open(png, "rb") as fr:
    #     png_bytes = fr.read()
    #
    # png_base64 = base64.b64encode(png_bytes).decode("utf-8")
    # png_md = f"![Image](data:image/png;base64,{png_base64})"

    # DOT
    dot = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.dot"
    graph.write(
        path=dot,
        format="dot",
    )

    # yield Output(
    #     output_name="docker_compose_landscape",
    #     value=graph,
    # )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "svg": MetadataValue.md(svg_md),
            # "png": MetadataValue.md(png_md),  # slow in Dagster UI
            "__".join(context.asset_key.path): MetadataValue.json(str(graph)),
            "svg_path": MetadataValue.path(svg),
            "png_path": MetadataValue.path(png),
            "dot_path": MetadataValue.path(dot),
        },
    )

    # graph.add_subgraph(
    #     pydot.graph_from_dot_data(docker_compose_graph_default.to_string())
    # )
    #
    # graph.add_subgraph(
    #     pydot.graph_from_dot_data(docker_compose_graph_worker.to_string())
    # )

    # s = ""
    # s += docker_compose_graph_default.to_string()
    # s += docker_compose_graph_worker.to_string()

    # graph = pydot.graph_from_dot_data(s)

    # context.log.info(docker_compose_graph_default)
    # context.log.info(docker_compose_graph_worker)
    context.log.info(graph)

    ret = {}

    # ret.update(
    #     {
    #         "COMPOSE_SCOPE": ComposeScope.DEFAULT,
    #     }
    # )

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


# # Dynamic inputs based on the imported
# # third party code locations
# ins = {}
# for i in THIRD_PARTY:
#     enabled = i["enabled"]
#     if not enabled:
#         continue
#     # ex: module = "OpenStudioLandscapes.Ayon.definitions"
#     module = i["module"]
#     compose_scope = i["compose_scope"]
#     if compose_scope == ComposeScope.DEFAULT:
#         split = module.split(".")
#         key = split[1]  # key = "Ayon"
#         ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))
#
#
# @asset(
#     **ASSET_HEADER_COMPOSE,
#     ins={
#         "env": AssetIn(
#             AssetKey([*KEY_COMPOSE, "env"]),
#         ),
#         **ins,
#     },
# )
# def compose(
#     context: AssetExecutionContext,
#     env: dict,  # pylint: disable=redefined-outer-name
#     **kwargs,
# ) -> Generator[
#     Output[dict[str, list[dict[str, list]]]] | AssetMaterialization, None, None
# ]:
#     """ """
#
#     context.log.info(kwargs)
#
#     _group_in = []
#
#     docker_compose = pathlib.PurePosixPath(
#         env["DOT_LANDSCAPES"],
#         env.get("LANDSCAPE", "default"),
#         f"{GROUP_COMPOSE_WORKER}__{'__'.join(KEY_COMPOSE_WORKER)}",
#         "__".join(context.asset_key.path),
#         "docker_compose",
#         "docker-compose.yml",
#     )
#
#     for v in kwargs.values():
#         _rel_path = os.path.relpath(
#             path=v.as_posix(),
#             start=docker_compose.parent.as_posix(),
#         )
#         rel_path = pathlib.Path(_rel_path)
#
#         _group_in.append(rel_path)
#
#     docker_dict = {
#         "include": [{"path": [i.as_posix()]} for i in _group_in],
#     }
#
#     docker_yaml = yaml.dump(docker_dict)
#
#     yield Output(docker_dict)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
#             "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
#         },
#     )
#
#
# group_out = AssetsDefinition.from_op(
#     op_group_out,
#     can_subset=True,
#     group_name=GROUP_COMPOSE,
#     key_prefix=KEY_COMPOSE,
#     keys_by_input_name={
#         "compose": AssetKey([*KEY_COMPOSE, "compose"]),
#         "env": AssetKey([*KEY_COMPOSE, "env"]),
#     },
# )
#
#
# docker_compose_graph = AssetsDefinition.from_op(
#     op_docker_compose_graph,
#     group_name=GROUP_COMPOSE,
#     key_prefix=KEY_COMPOSE,
#     keys_by_input_name={
#         "group_out": AssetKey([*KEY_COMPOSE, "group_out"]),
#         "compose_project_name": AssetKey([*KEY_COMPOSE, "compose_project_name"]),
#     },
# )
