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

    docker_compose_dir = compose_10_2.parent / context.asset_key.path[-1]

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    png = docker_compose_dir / f"{context.asset_key.path[-1]}.png"
    dcg.graph.write(
        path=png,
        format="png",
    )

    with open(png, "rb") as fr:
        png_bytes = fr.read()

    png_base64 = base64.b64encode(png_bytes).decode("utf-8")
    png_md = f"![Image](data:image/svg+xml;base64,{png_base64})"

    dot = docker_compose_dir / f"{context.asset_key.path[-1]}.dot"
    dcg.graph.write(
        path=dot,
        format="dot",
    )

    yield Output(dcg.graph)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[-1]: MetadataValue.json(str(dcg.graph)),
            "png": MetadataValue.md(png_md),
            "dot_path": MetadataValue.path(dot),
            "png_path": MetadataValue.path(png),
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

    docker_compose_dir = compose_repository_10_2.parent / context.asset_key.path[-1]

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    png = docker_compose_dir / f"{context.asset_key.path[-1]}.png"
    dcg.graph.write(
        path=docker_compose_dir / f"{context.asset_key.path[-1]}.png",
        format="png",
    )

    with open(png, "rb") as fr:
        png_bytes = fr.read()

    png_base64 = base64.b64encode(png_bytes).decode("utf-8")
    png_md = f"![Image](data:image/svg+xml;base64,{png_base64})"

    dot = docker_compose_dir / f"{context.asset_key.path[-1]}.dot"
    dcg.graph.write(
        path=docker_compose_dir / f"{context.asset_key.path[-1]}.dot",
        format="dot",
    )

    yield Output(dcg.graph)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[-1]: MetadataValue.json(str(dcg.graph)),
            "png": MetadataValue.md(png_md),
            "dot_path": MetadataValue.path(dot),
            "png_path": MetadataValue.path(png),
        },
    )
