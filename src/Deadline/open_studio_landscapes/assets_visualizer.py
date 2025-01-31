import base64
import pydot
import pathlib

from docker_graph.docker_graph import DockerComposeGraph

from dagster import (
    asset,
    AssetIn,
    AssetExecutionContext,
    Output,
    AssetMaterialization,
    MetadataValue,
)


@asset(
    group_name="Viz",
    compute_kind="python",
    key_prefix=[
        "10_2",
    ],
    ins={
        "compose_10_2": AssetIn(
            key_prefix=[
                "10_2",
            ],
        ),
    },
)
def viz_compose_10_2(
        context: AssetExecutionContext,
        compose_10_2: pathlib.Path,
) -> pydot.Dot:
    """
    """

    dcg = DockerComposeGraph()
    trees = dcg.parse_docker_compose(
        pathlib.Path(compose_10_2)
    )

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = compose_10_2.parent / '__'.join(context.asset_key.path)

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
            '__'.join(context.asset_key.path): MetadataValue.json(str(dcg.graph)),
            "svg": MetadataValue.md(svg_md),
            "dot_path": MetadataValue.path(dot),
            "svg_path": MetadataValue.path(svg),
        },
    )


@asset(
    group_name="Viz",
    compute_kind="python",
    key_prefix=[
        "10_2",
    ],
    ins={
        "compose_repository_10_2": AssetIn(
            key_prefix=[
                "10_2",
            ],
        ),
    },
)
def viz_compose_repository_10_2(
        context: AssetExecutionContext,
        compose_repository_10_2: pathlib.Path,
) -> pydot.Dot:
    """
    """

    dcg = DockerComposeGraph()
    trees = dcg.parse_docker_compose(
        pathlib.Path(compose_repository_10_2)
    )

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = compose_repository_10_2.parent / '__'.join(context.asset_key.path)

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
            '__'.join(context.asset_key.path): MetadataValue.json(str(dcg.graph)),
            "svg": MetadataValue.md(svg_md),
            "dot_path": MetadataValue.path(dot),
            "svg_path": MetadataValue.path(svg),
        },
    )
