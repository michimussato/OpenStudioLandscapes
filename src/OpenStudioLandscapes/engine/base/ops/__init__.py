import base64
import pathlib
import shlex
import shutil
from typing import Generator

import pydot
import yaml
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
#
# from OpenStudioLandscapes.engine.constants import ComposeScope
#
#
# @op(
#     name="compose_scope",
#     out={
#         "compose_scope": Out(ComposeScope),
#     },
# )
# def op_compose_scope(
#     context: OpExecutionContext,
#     compose_scope: pathlib.Path,  # pylint: disable=redefined-outer-name
# ) -> Generator[Output[ComposeScope] | AssetMaterialization, None, None]:
#     """ """
#
#     compose_scope_value = ComposeScope
#
#     yield Output(Comp)
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


@op(
    name="docker_compose_graph",
    ins={
        "group_out": In(),
    },
)
def op_docker_compose_graph(
    context: OpExecutionContext,
    group_out: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pydot.Dot] | AssetMaterialization, None, None]:
    """ """

    dcg = DockerComposeGraph()
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


@op(
    name="group_out",
    # tags={
    #     "domain": "marketing",
    # },
    ins={
        "compose": In(dict),
        "env": In(dict),
        # "compose_scope": In(ComposeScope),
    },
    out={
        "group_out": Out(pathlib.Path),
    },
)
def op_group_out(
    context: OpExecutionContext,
    compose: dict,  # pylint: disable=redefined-outer-name
    env: dict,  # pylint: disable=redefined-outer-name
    # compose_scope: ComposeScope,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    docker_yaml = yaml.dump(compose)

    group_names_by_key_dict = (
        context.assets_def.group_names_by_key
    )  # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
    asset_key = context.assets_def.key  # AssetKey(['OpenCue', 'group_out'])
    group = group_names_by_key_dict[asset_key]

    # Todo:
    #  Maybe there is a better way but it does not matter yet
    #  as long as there are only AssetKey([PREFIX, KEY]) with
    #  no sub-prefixes inbetween
    key = context.asset_key.path[0]

    context.log.info(group_names_by_key_dict)
    context.log.info(group)
    # context.log.info(key)

    docker_compose = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{group}__{key}",
        "__".join(context.asset_key.path),
        "docker_compose",
        "docker-compose.yml",
    )

    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, mode="w", encoding="utf-8") as fw:
        fw.write(docker_yaml)

    # project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{ComposeScope.value}"
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

    yield Output(
        output_name="group_out",
        value=docker_compose,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
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
        },
    )


# @op(
#     name="group_out_dummy",
#     # tags={
#     #     "domain": "marketing",
#     # },
#     out={
#         "group_out": Out(None),
#     },
#     description="Dummy Out. Returns `None`",
# )
# def op_group_out_dummy(
#     context: OpExecutionContext,
# ) -> Output[None]:
#
#     return Output(
#         output_name="group_out",
#         value=None,
#     )


# @op(
#     name="group_out",
#     # tags={
#     #     "domain": "marketing",
#     # },
#     ins={
#         "compose": In(dict),
#         "env": In(dict),
#     },
#     out={
#         "group_out": Out(None),
#         "group_out_bypass": Out(pathlib.Path),
#     },
# )
# def op_group_out_with_dummy(
#     context: OpExecutionContext,
#     compose: dict,  # pylint: disable=redefined-outer-name
#     env: dict,  # pylint: disable=redefined-outer-name
# ) -> Generator[Output[None | pathlib.Path] | AssetMaterialization, None, None]:
#
#     docker_yaml = yaml.dump(compose)
#
#     group_names_by_key_dict = (
#         context.assets_def.group_names_by_key
#     )  # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
#     asset_key = context.assets_def.key  # AssetKey(['OpenCue', 'group_out'])
#     group = group_names_by_key_dict[asset_key]
#
#     # Todo:
#     #  Maybe there is a better way but it does not matter yet
#     #  as long as there are only AssetKey([PREFIX, KEY]) with
#     #  no sub-prefixes inbetween
#     key = context.asset_key.path[0]
#
#     context.log.info(group_names_by_key_dict)
#     context.log.info(group)
#     # context.log.info(key)
#
#     docker_compose = pathlib.Path(
#         env["DOT_LANDSCAPES"],
#         env.get("LANDSCAPE", "default"),
#         f"{group}__{key}",
#         "__".join(context.asset_key.path),
#         "docker_compose",
#         "docker-compose.yml",
#     )
#
#     docker_compose.parent.mkdir(parents=True, exist_ok=True)
#
#     with open(docker_compose, mode="w", encoding="utf-8") as fw:
#         fw.write(docker_yaml)
#
#     project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}"
#
#     cmd_docker_compose_up = [
#         shutil.which("docker"),
#         "compose",
#         "--file",
#         docker_compose.as_posix(),
#         "--project-name",
#         project_name,
#         "up",
#         "--remove-orphans",
#     ]
#
#     cmd_docker_compose_pull_up = [
#         shutil.which("docker"),
#         "compose",
#         "--file",
#         docker_compose.as_posix(),
#         "--project-name",
#         project_name,
#         "pull",
#         "--ignore-pull-failures",
#         "&&",
#         *cmd_docker_compose_up,
#     ]
#
#     cmd_docker_compose_down = [
#         shutil.which("docker"),
#         "compose",
#         "--file",
#         docker_compose.as_posix(),
#         "--project-name",
#         project_name,
#         "down",
#         "--remove-orphans",
#     ]
#
#     yield Output(
#         output_name="group_out",
#         value=None,
#     )
#
#     yield Output(
#         output_name="group_out_bypass",
#         value=docker_compose,
#     )
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
#             "cmd_docker_compose_up": MetadataValue.path(
#                 " ".join(shlex.quote(s) for s in cmd_docker_compose_up)
#             ),
#             "cmd_docker_compose_pull_up": MetadataValue.path(
#                 " ".join(
#                     shlex.quote(s) if not s in ["&&", ";"] else s
#                     for s in cmd_docker_compose_pull_up
#                 )
#             ),
#             "cmd_docker_compose_down": MetadataValue.path(
#                 " ".join(shlex.quote(s) for s in cmd_docker_compose_down)
#             ),
#             "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
#         },
#     )
