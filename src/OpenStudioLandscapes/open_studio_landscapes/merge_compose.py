import pathlib
import yaml
import shutil
import shlex
import copy
from collections import ChainMap
from functools import reduce
import pydot
import base64
from docker_compose_graph.docker_compose_graph import DockerComposeGraph

from docker_compose_graph.utils import *

from dagster import (
    asset,
    AssetIn,
    AssetKey,
    AssetExecutionContext,
    Output,
    AssetMaterialization,
    MetadataValue,
)

from OpenStudioLandscapes.open_studio_landscapes.assets import KEY as KEY_BASE
from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2.assets import KEY as KEY_DEADLINE_10_2


GROUP = "Merge_And_Finalize"
KEY = "Merge_And_Finalize"

asset_header = {
    "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python",
}


@asset(
    **asset_header,
    ins={
        "compose_base": AssetIn(
            AssetKey([KEY_BASE, "compose"]),
        ),
        "group_out_deadline_10_2": AssetIn(AssetKey([KEY_DEADLINE_10_2, "group_out"])),
    },
)
def docker_compose_merge(
    context: AssetExecutionContext,
    compose_base: dict,  # pylint: disable=redefined-outer-name
    group_out_deadline_10_2: dict,  # pylint: disable=redefined-outer-name
) -> dict:

    docker_chainmap = ChainMap(
        copy.deepcopy(compose_base),
        copy.deepcopy(group_out_deadline_10_2),
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY_BASE, "env"]),
        ),
        "docker_compose_merge": AssetIn(
            AssetKey([KEY, "docker_compose_merge"]),
        ),
    },
)
def docker_compose_write(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    docker_compose_merge: dict,  # pylint: disable=redefined-outer-name
) -> pathlib.Path:
    """ """

    docker_yaml = yaml.dump(docker_compose_merge)

    docker_compose = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        KEY,
        "docker_compose",
        "__".join(context.asset_key.path),
        "docker-compose.yml",
    )

    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}"

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "up",
        "--remove-orphans",
    ]

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "down",
        "--remove-orphans",
    ]

    yield Output(docker_compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
            "cmd_docker_compose_up": MetadataValue.path(
                " ".join(shlex.quote(s) for s in cmd_docker_compose_up)
            ),
            "cmd_docker_compose_down": MetadataValue.path(
                " ".join(shlex.quote(s) for s in cmd_docker_compose_down)
            ),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )


@asset(
    **asset_header,
    ins={
        "docker_compose_write": AssetIn(
            AssetKey([KEY, "docker_compose_write"]),
        ),
    },
)
def docker_compose_graph(
    context: AssetExecutionContext,
    docker_compose_write: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> pydot.Dot:
    """ """

    dcg = DockerComposeGraph()
    trees = dcg.parse_docker_compose(pathlib.Path(docker_compose_write))

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = docker_compose_write.parent / "__".join(context.asset_key.path)

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    # SVG
    svg = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.svg"
    dcg.graph.write(
        path=svg,
        format="svg",
    )

    with open(svg, "rb") as fr:
        svg_bytes = fr.read()

    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
    svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"

    # PNG
    png = docker_compose_dir / f"{'__'.join(context.asset_key.path)}.png"
    dcg.graph.write(
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
    dcg.graph.write(
        path=dot,
        format="dot",
    )

    yield Output(dcg.graph)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "svg": MetadataValue.md(svg_md),
            # "png": MetadataValue.md(png_md),  # slow in Dagster UI
            "__".join(context.asset_key.path): MetadataValue.json(str(dcg.graph)),
            "svg_path": MetadataValue.path(svg),
            "png_path": MetadataValue.path(png),
            "dot_path": MetadataValue.path(dot),
        },
    )
