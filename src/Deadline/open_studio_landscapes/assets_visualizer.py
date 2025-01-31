import base64
import pydot
import pathlib

from docker_graph.docker_graph import DockerComposeGraph

from dagster import (
    asset,
    AssetIn,
    AssetKey,
    AssetExecutionContext,
    Output,
    AssetMaterialization,
    MetadataValue,
)


from Deadline.open_studio_landscapes.assets_10_2 import KEY as KEY_10_2


GROUP = "Viz"
KEY = "Viz"

asset_header = {
    "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python"
}


@asset(
    **asset_header,
    ins={
        "compose": AssetIn(
            AssetKey([KEY_10_2, "compose_10_2"]),
        ),
    },
)
def viz_compose_10_2(
        context: AssetExecutionContext,
        compose: pathlib.Path,
) -> pydot.Dot:
    """
    """

    dcg = DockerComposeGraph()
    trees = dcg.parse_docker_compose(
        pathlib.Path(compose)
    )

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = compose.parent / '__'.join(context.asset_key.path)

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    svg = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.svg"
    dcg.graph.write(
        path=svg,
        format="svg",
    )

    with open(svg, "rb") as fr:
        svg_bytes = fr.read()

    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
    svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"

    dot = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.dot"
    dcg.graph.write(
        path=dot,
        format="dot",
    )

    yield Output(dcg.graph)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "svg": MetadataValue.md(svg_md),
            "__".join(context.asset_key.path): MetadataValue.json(str(dcg.graph)),
            "svg_path": MetadataValue.path(svg),
            "dot_path": MetadataValue.path(dot),
        },
    )


@asset(
    **asset_header,
    ins={
        "compose_repository": AssetIn(
            AssetKey([KEY_10_2, "compose_repository_10_2"]),
        ),
    },
)
def viz_compose_repository_10_2(
        context: AssetExecutionContext,
        compose_repository: pathlib.Path,
) -> pydot.Dot:
    """
    """

    dcg = DockerComposeGraph()
    trees = dcg.parse_docker_compose(
        pathlib.Path(compose_repository)
    )

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = compose_repository.parent / '__'.join(context.asset_key.path)

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    svg = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.svg"
    dcg.graph.write(
        path=svg,
        format="svg",
    )

    with open(svg, "rb") as fr:
        svg_bytes = fr.read()

    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
    svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"

    dot = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.dot"
    dcg.graph.write(
        path=docker_compose_dir / f"{'__'.join(context.asset_key.path)}.dot",
        format="dot",
    )

    yield Output(dcg.graph)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "svg": MetadataValue.md(svg_md),
            "__".join(context.asset_key.path): MetadataValue.json(str(dcg.graph)),
            "svg_path": MetadataValue.path(svg),
            "dot_path": MetadataValue.path(dot),
        },
    )
