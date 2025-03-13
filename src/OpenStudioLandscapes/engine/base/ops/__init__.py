import base64
import copy
import os
import pathlib
import shlex
import shutil
from collections import ChainMap
from functools import reduce
from typing import Generator, MutableMapping

import yaml
from dagster._core.definitions import asset_key
from docker_compose_graph.utils import *
import pydot

from dagster import (
    AssetMaterialization,
    In,
    MetadataValue,
    OpExecutionContext,
    Out,
    Output,
    op,
)

from docker_compose_graph.docker_compose_graph import DockerComposeGraph


@op(
    name="compose",
    ins={
        "compose_networks": In(dict),
        "compose_maps": In(list),
    },
    out={
        "compose": Out(dict),
    },
)
def op_compose(
    context: OpExecutionContext,
    compose_networks: dict,  # pylint: disable=redefined-outer-name
    # **kwargs,  # pylint: disable=redefined-outer-name
    compose_maps: list[dict],  # pylint: disable=redefined-outer-name
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    if "networks" in compose_networks:
        network_dict = copy.deepcopy(compose_networks)
    else:
        network_dict = {}

    docker_chainmap = ChainMap(
        network_dict,
        *compose_maps,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)

    docker_yaml = yaml.dump(docker_dict)

    yield Output(
        output_name="compose",
        value=docker_dict,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


@op(
    name="docker_compose_graph",
    ins={
        "group_out": In(pathlib.Path),
        "compose_project_name": In(str),
    },
    out={
        "docker_compose_graph": Out(pydot.Dot),
    },
)
def op_docker_compose_graph(
    context: OpExecutionContext,
    group_out: pathlib.Path,  # pylint: disable=redefined-outer-name
    compose_project_name: str,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pydot.Dot] | AssetMaterialization, None, None]:
    """ """

    dcg = DockerComposeGraph(
        # label_root_service=
    )
    trees = dcg.parse_docker_compose(pathlib.Path(group_out))

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = group_out.parent / "__".join(context.asset_key.path)

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

    yield Output(
        output_name="docker_compose_graph",
        value=dcg.graph,
    )

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


@op(
    # can_subset=True,
    name="group_out",
    ins={
        "compose": In(dict),
        "env": In(dict),
    },
    out={
        "group_out": Out(pathlib.Path),
        "compose_project_name": Out(str),
    },
)
def op_group_out(
    context: OpExecutionContext,
    compose: dict,  # pylint: disable=redefined-outer-name
    env: dict,  # pylint: disable=redefined-outer-name
    # compose_scope: ComposeScope,
) -> Generator[Output[pathlib.Path] | Output[str] | AssetMaterialization, None, None]:

    docker_yaml = yaml.dump(compose)

    context.log.warning(context.asset_key_for_output("group_out"))
    context.log.warning(context.asset_key_for_output("compose_project_name"))
    context.log.warning(context.selected_output_names)

    group_names_by_key_dict = (
        context.assets_def.group_names_by_key
    )
    # Results in:
    # Single Output:
    # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
    # Multiple Outputs:
    # {AssetKey(['Compose_default', 'group_out']): 'Compose_default', AssetKey(['Compose_default', 'compose_project_name']): 'Compose_default'}
    context.log.warning(group_names_by_key_dict)
    asset_key_group_out = context.asset_key_for_output("group_out")  # AssetKey(['OpenCue', 'group_out'])
    group_group_out = group_names_by_key_dict[asset_key_group_out]

    # Todo:
    #  Maybe there is a better way but it does not matter yet
    #  as long as there are only AssetKey([PREFIX, KEY]) with
    #  no sub-prefixes inbetween
    key_group_out = context.asset_key_for_output("group_out").path[0]

    docker_compose = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{group_group_out}__{key_group_out}",
        "__".join(context.asset_key_for_output("group_out").path),
        "docker_compose",
        "docker-compose.yml",
    )

    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, mode="w", encoding="utf-8") as fw:
        fw.write(docker_yaml)

    project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{env['COMPOSE_SCOPE']}"

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
    script_cmd_docker_compose_up = docker_compose.parent / "docker_compose_up.sh"

    cmd_docker_compose_pull_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "pull",
        "--ignore-pull-failures",
        "&&",
        *cmd_docker_compose_up,
    ]
    script_cmd_docker_compose_pull_up = docker_compose.parent / "docker_compose_pull_up.sh"

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
    script_cmd_docker_compose_down = docker_compose.parent / "docker_compose_down.sh"

    docker_script = dict()
    scripts = []

    docker_script["exe"] = shutil.which("bash")
    docker_script["script"] = str()

    docker_script["script"] += f"#!{docker_script['exe']}\n"
    docker_script["script"] += f"# AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key_for_output('group_out').path)}\n"
    docker_script["script"] += "\n"
    docker_script["script"] += "SCRIPT_DIR=$( cd -- \"$( dirname -- \"${BASH_SOURCE[0]}\" )\" &> /dev/null && pwd )\n"
    docker_script["script"] += "\n"

    with open(
        file=script_cmd_docker_compose_up,
        mode="w",
        encoding="utf-8",
    ) as fw:
        fw.write(docker_script["script"])
        fw.write(f"{shlex.join(cmd_docker_compose_up)}\n".replace(docker_compose.parent.as_posix(), '"${SCRIPT_DIR}"'))
        fw.write("\n")
        fw.write("exit 0;\n")
    os.chmod(
        script_cmd_docker_compose_up,
        mode=os.stat(script_cmd_docker_compose_up).st_mode | 0o111,
    )
    scripts.append(script_cmd_docker_compose_up.as_posix())

    with open(
        file=script_cmd_docker_compose_pull_up,
        mode="w",
        encoding="utf-8",
    ) as fw:
        fw.write(docker_script["script"])
        fw.write(f"{shlex.join(cmd_docker_compose_pull_up)}\n".replace(docker_compose.parent.as_posix(), '"${SCRIPT_DIR}"'))
        fw.write("\n")
        fw.write("exit 0;\n")
    os.chmod(
        script_cmd_docker_compose_pull_up,
        mode=os.stat(script_cmd_docker_compose_pull_up).st_mode | 0o111,
    )
    scripts.append(script_cmd_docker_compose_pull_up.as_posix())

    with open(
        file=script_cmd_docker_compose_down,
        mode="w",
        encoding="utf-8",
    ) as fw:
        fw.write(docker_script["script"])
        fw.write(f"{shlex.join(cmd_docker_compose_down)}\n".replace(docker_compose.parent.as_posix(), '"${SCRIPT_DIR}"'))
        fw.write("\n")
        fw.write("exit 0;\n")
    os.chmod(
        script_cmd_docker_compose_down,
        mode=os.stat(script_cmd_docker_compose_down).st_mode | 0o111,
    )
    scripts.append(script_cmd_docker_compose_down.as_posix())

    if "group_out" in context.selected_output_names:
        yield Output(
            output_name="group_out",
            value=docker_compose,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("group_out"),
            metadata={
                "__".join(context.asset_key_for_output("group_out").path): MetadataValue.path(docker_compose),
                "root_dir": MetadataValue.path(docker_compose.parent),
                "cmd_docker_compose_up": MetadataValue.path(
                    " ".join(shlex.quote(s) for s in cmd_docker_compose_up)
                ),
                "cmd_docker_compose_pull_up": MetadataValue.path(
                    " ".join(
                        shlex.quote(s) if not s in ["&&", ";"] else s
                        for s in cmd_docker_compose_pull_up
                    )
                ),
                "cmd_docker_compose_down": MetadataValue.path(
                    " ".join(shlex.quote(s) for s in cmd_docker_compose_down)
                ),
                "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
                "scripts": MetadataValue.json(scripts),
            },
        )

    if "compose_project_name" in context.selected_output_names:
        yield Output(
            output_name="compose_project_name",
            value=project_name,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("compose_project_name"),
            metadata={
                "__".join(context.asset_key_for_output("compose_project_name").path): MetadataValue.text(project_name),
            },
        )
