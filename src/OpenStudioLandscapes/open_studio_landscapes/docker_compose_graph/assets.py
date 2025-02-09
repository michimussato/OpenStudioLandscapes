import base64
import pathlib

import pydot
from docker_compose_graph.docker_compose_graph import DockerComposeGraph

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)
from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2.assets import (
    KEY as KEY_DEADLINE_V10_2,
)

GROUP = "Docker_Compose_Graph"
KEY = "Docker_Compose_Graph"

asset_header = {"group_name": GROUP, "key_prefix": [KEY], "compute_kind": "python"}

# @asset(
#     **asset_header,
#     ins={
#         "compose_repository_10_2": AssetIn(
#             AssetKey([KEY_DEADLINE_V10_2, "compose_repository"]),
#         ),
#     },
# )
# def docker_compose_graph_repository_10_2(
#     context: AssetExecutionContext,
#     compose_repository_10_2: pathlib.Path,  # pylint: disable=redefined-outer-name
# ) -> pydot.Dot:
#     """ """
#
#     dcg = DockerComposeGraph()
#     trees = dcg.parse_docker_compose(pathlib.Path(compose_repository_10_2))
#
#     context.log.info(trees)
#
#     dcg.iterate_trees(trees)
#
#     docker_compose_dir = compose_repository_10_2.parent / "__".join(
#         context.asset_key.path
#     )
#
#     docker_compose_dir.mkdir(parents=True, exist_ok=True)
#
#     # SVG
#     svg = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.svg"
#     dcg.graph.write(
#         path=svg,
#         format="svg",
#     )
#
#     with open(svg, "rb") as fr:
#         svg_bytes = fr.read()
#
#     svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
#     svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"
#
#     # PNG
#     png = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.png"
#     dcg.graph.write(
#         path=png,
#         format="png",
#     )
#
#     # SLOW
#     # with open(png, "rb") as fr:
#     #     png_bytes = fr.read()
#     #
#     # png_base64 = base64.b64encode(png_bytes).decode("utf-8")
#     # png_md = f"![Image](data:image/png;base64,{png_base64})"
#
#     # DOT
#     dot = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.dot"
#     dcg.graph.write(
#         path=docker_compose_dir / f"{'__'.join(context.asset_key.path)}.dot",
#         format="dot",
#     )
#
#     yield Output(dcg.graph)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "svg": MetadataValue.md(svg_md),
#             # "png": MetadataValue.md(png_md),  # slow in Dagster UI
#             "__".join(context.asset_key.path): MetadataValue.json(str(dcg.graph)),
#             "svg_path": MetadataValue.path(svg),
#             "png_path": MetadataValue.path(png),
#             "dot_path": MetadataValue.path(dot),
#         },
#     )
