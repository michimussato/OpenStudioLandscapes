__all__ = [
    "op_group_out",
    "op_docker_compose_graph",
]

import base64
import os
import pathlib
import shlex
import shutil
from typing import Generator, List, MutableMapping, Union

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

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.config.models import (
    FeatureBaseModel,
    ComposeScopeBaseModel,
)


# Todo
#  - [ ] convert to factory
@op(
    name="op_docker_config_json",
    ins={
        "group_in": In(dict),
    },
    out={
        "docker_config_json": Out(pathlib.Path),
    },
)
def op_docker_config_json(
    context: OpExecutionContext,
    group_in: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
    """
    Provides a Feature with the `docker_config_json` pathlib.Path.
    """

    docker_config_json = group_in.pop("docker_config_json")

    yield Output(
        output_name="docker_config_json",
        value=docker_config_json,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(docker_config_json),
        },
    )


# Todo
#  - [ ] convert to factory
@op(
    name="docker_compose_graph",
    ins={
        "group_out": In(pathlib.Path),
        "compose_project_name": In(str),
    },
    out={
        "docker_compose_graph": Out(pydot.Dot),
        "docker_compose_graph_dot": Out(pathlib.Path),
    },
)
def op_docker_compose_graph(
    context: OpExecutionContext,
    group_out: pathlib.Path,  # pylint: disable=redefined-outer-name
    compose_project_name: str,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[pydot.Dot] | Output[pathlib.Path] | AssetMaterialization, None, None
]:
    """ """

    dcg = DockerComposeGraph(
        label_root_service=compose_project_name,
    )
    trees = dcg.parse_docker_compose(pathlib.Path(group_out))

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = group_out.parent / "__".join(
        context.asset_key_for_output("docker_compose_graph").path
    )

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    # SVG
    svg = (
        docker_compose_dir
        / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.svg"
    )
    try:
        dcg.graph.write(
            path=svg,
            format="svg",
        )
    except FileNotFoundError as e:
        context.log.error(e)
        raise FileNotFoundError("Is Graphviz installed?") from e

    with open(svg, "rb") as fr:
        svg_bytes = fr.read()

    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
    svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"

    # PNG
    png = (
        docker_compose_dir
        / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.png"
    )
    try:
        dcg.graph.write(
            path=png,
            format="png",
        )
    except FileNotFoundError as e:
        context.log.error(e)
        raise FileNotFoundError("Is Graphviz installed?") from e

    # SLOW
    # with open(png, "rb") as fr:
    #     png_bytes = fr.read()
    #
    # png_base64 = base64.b64encode(png_bytes).decode("utf-8")
    # png_md = f"![Image](data:image/png;base64,{png_base64})"

    # DOT
    dot = (
        docker_compose_dir
        / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.dot"
    )
    try:
        dcg.graph.write(
            path=dot,
            format="dot",
        )
    except FileNotFoundError as e:
        context.log.error(e)
        raise FileNotFoundError("Is Graphviz installed?") from e

    ########################
    # DOCKER_COMPOSE_GRAPH #
    ########################

    # if "docker_compose_graph" in context.selected_output_names:

    yield Output(
        output_name="docker_compose_graph",
        value=dcg.graph,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("docker_compose_graph"),
        metadata={
            "svg": MetadataValue.md(svg_md),
            "__".join(
                context.asset_key_for_output("docker_compose_graph").path
            ): MetadataValue.json(str(dcg.graph)),
            "svg_path": MetadataValue.path(svg),
            "png_path": MetadataValue.path(png),
        },
    )

    ############################
    # DOCKER_COMPOSE_GRAPH_DOT #
    ############################

    # if "docker_compose_graph_dot" in context.selected_output_names:

    yield Output(
        output_name="docker_compose_graph_dot",
        value=dot,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("docker_compose_graph_dot"),
        metadata={
            "__".join(
                context.asset_key_for_output("docker_compose_graph_dot").path
            ): MetadataValue.path(dot),
        },
    )


# Todo
#  - [ ] What is not needed anymore?
#  - [ ] convert to factory
# def factory_group_out(
#     name="op_group_out_factory",
#     ins=None,
#     **kwargs,
# ) -> OpDefinition:
#
#     @op(
#         name=name,
#         ins=ins,
#         **kwargs,
#     )
#     def _op_group_out(
#         context: OpExecutionContext,
#         **kwargs,
#     ):
#         """
#         Provides a Feature with the `env` dict.
#         """
#
#         # compose = kwargs.pop("compose")
#         env = kwargs.pop("env")
#         docker_config = kwargs.pop("docker_config")
#
#         DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
#         # Todo:
#         #  - [ ] Is this necessary here?
#         DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)
#
#         context.log.debug(context.asset_key_for_output("group_out"))
#         context.log.debug(context.asset_key_for_output("compose_project_name"))
#         context.log.debug(context.selected_output_names)
#
#         build_base_docker_config: DockerConfig = docker_config
#         build_base_docker_config_value = build_base_docker_config.value
#
#         compose_project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{env['COMPOSE_SCOPE']}"
#
#         group_names_by_key_dict = (
#             context.assets_def.group_names_by_key
#         )
#         # Results in:
#         # Single Output:
#         # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
#         # Multiple Outputs:
#         # {AssetKey(['Compose_default', 'group_out']): 'Compose_default', AssetKey(['Compose_default', 'compose_project_name']): 'Compose_default'}
#         context.log.debug(group_names_by_key_dict)
#
#         cmd_docker_compose_up = [
#             shutil.which("docker"),
#             "compose",
#             "--file",
#             DOCKER_COMPOSE.as_posix(),
#             "--project-name",
#             compose_project_name,
#             "up",
#             "--remove-orphans",
#         ]
#         script_cmd_docker_compose_up = DOCKER_COMPOSE.parent / "docker_compose_up.sh"
#
#         cmd_docker_compose_logs = [
#             shutil.which("docker"),
#             "compose",
#             "--file",
#             DOCKER_COMPOSE.as_posix(),
#             "--project-name",
#             compose_project_name,
#             "logs",
#             "--follow",
#         ]
#         script_cmd_docker_compose_logs = DOCKER_COMPOSE.parent / "docker_compose_logs.sh"
#
#         cmd_docker_compose_pull_up = [
#             shutil.which("docker"),
#             "compose",
#             "--file",
#             DOCKER_COMPOSE.as_posix(),
#             "--project-name",
#             compose_project_name,
#             "pull",
#             "--ignore-pull-failures",
#             "&&",
#             *cmd_docker_compose_up,
#         ]
#         script_cmd_docker_compose_pull_up = DOCKER_COMPOSE.parent / "docker_compose_pull_up.sh"
#
#         cmd_docker_compose_down = [
#             shutil.which("docker"),
#             "compose",
#             "--file",
#             DOCKER_COMPOSE.as_posix(),
#             "--project-name",
#             compose_project_name,
#             "down",
#             "--remove-orphans",
#         ]
#         script_cmd_docker_compose_down = DOCKER_COMPOSE.parent / "docker_compose_down.sh"
#
#         # Todo
#         #  cmd_docker_exec_it = [
#         #      shutil.which("docker"),
#         #      "exec",
#         #      "--tty",
#         #      "--interactive",
#         #      "sh",  # or bash
#         #  ]
#         #  script_cmd_docker_exec_it = DOCKER_COMPOSE.parent / "docker_exec.sh"
#
#         # In case we need to log in to the registry
#         if not build_base_docker_config_value["docker_use_local"]:
#
#             if build_base_docker_config_value["docker_repository_type"] == DockerRepositoryType.PRIVATE:
#
#                 server = build_base_docker_config_value["docker_registry_url"]
#                 username = build_base_docker_config_value.get("docker_registry_username", None)
#                 password = build_base_docker_config_value.get("docker_registry_password", None)
#
#                 if not all([username, password]):
#                     raise Exception("Both username and password are required")
#
#                 cmd_docker_login = [
#                     shutil.which("docker"),
#                     "login",
#                     "--username", username,
#                     "--password", password,
#                     server,
#                 ]
#
#                 cmd_docker_logout = [
#                     shutil.which("docker"),
#                     "logout",
#                 ]
#
#                 cmd_docker_compose_up = [
#                     *cmd_docker_login,
#                     "&&",
#                     *cmd_docker_compose_up,
#                     "&&",
#                     *cmd_docker_logout,
#                 ]
#
#                 cmd_docker_compose_pull_up =  [
#                     *cmd_docker_login,
#                     "&&",
#                     *cmd_docker_compose_pull_up,
#                     "&&",
#                     *cmd_docker_logout,
#                 ]
#
#         docker_script = dict()
#         scripts = []
#
#         docker_script["exe"] = shutil.which("bash")
#         docker_script["script"] = str()
#
#         docker_script["script"] += f"#!{docker_script['exe']}\n"
#         docker_script["script"] += f"# AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key_for_output('group_out').path)}\n"
#         docker_script["script"] += "\n"
#         docker_script["script"] += "SCRIPT_DIR=$( cd -- \"$( dirname -- \"${BASH_SOURCE[0]}\" )\" &> /dev/null && pwd )\n"
#         docker_script["script"] += "\n"
#
#         with open(
#             file=script_cmd_docker_compose_up,
#             mode="w",
#             encoding="utf-8",
#         ) as fw:
#             fw.write(docker_script["script"])
#             fw.write(f"{shlex.join(cmd_docker_compose_up)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
#             fw.write("\n")
#             fw.write("exit 0;\n")
#         os.chmod(
#             script_cmd_docker_compose_up,
#             mode=os.stat(script_cmd_docker_compose_up).st_mode | 0o111,
#         )
#         scripts.append(script_cmd_docker_compose_up.as_posix())
#
#         with open(
#             file=script_cmd_docker_compose_pull_up,
#             mode="w",
#             encoding="utf-8",
#         ) as fw:
#             fw.write(docker_script["script"])
#             fw.write(f"{shlex.join(cmd_docker_compose_pull_up)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
#             fw.write("\n")
#             fw.write("exit 0;\n")
#         os.chmod(
#             script_cmd_docker_compose_pull_up,
#             mode=os.stat(script_cmd_docker_compose_pull_up).st_mode | 0o111,
#         )
#         scripts.append(script_cmd_docker_compose_pull_up.as_posix())
#
#         with open(
#             file=script_cmd_docker_compose_down,
#             mode="w",
#             encoding="utf-8",
#         ) as fw:
#             fw.write(docker_script["script"])
#             fw.write(f"{shlex.join(cmd_docker_compose_down)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
#             fw.write("\n")
#             fw.write("exit 0;\n")
#         os.chmod(
#             script_cmd_docker_compose_down,
#             mode=os.stat(script_cmd_docker_compose_down).st_mode | 0o111,
#         )
#         scripts.append(script_cmd_docker_compose_down.as_posix())
#
#         with open(
#             file=script_cmd_docker_compose_logs,
#             mode="w",
#             encoding="utf-8",
#         ) as fw:
#             fw.write(docker_script["script"])
#             fw.write(f"{shlex.join(cmd_docker_compose_logs)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
#             fw.write("\n")
#             fw.write("exit 0;\n")
#         os.chmod(
#             script_cmd_docker_compose_logs,
#             mode=os.stat(script_cmd_docker_compose_logs).st_mode | 0o111,
#         )
#         scripts.append(script_cmd_docker_compose_logs.as_posix())
#
#         if "group_out" in context.selected_output_names:
#
#             # Todo
#             #  - [ ] rename to a more descriptive name
#             #############
#             # GROUP_OUT #
#             #############
#
#             yield Output(
#                 output_name="group_out",
#                 value=DOCKER_COMPOSE,
#             )
#
#             yield AssetMaterialization(
#                 asset_key=context.asset_key_for_output("group_out"),
#                 metadata={
#                     "__".join(context.asset_key_for_output("group_out").path): MetadataValue.path(DOCKER_COMPOSE),
#                     "root_dir": MetadataValue.path(DOCKER_COMPOSE.parent),
#                     # "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
#                     "scripts": MetadataValue.json(scripts),
#                 },
#             )
#
#         if "compose_project_name" in context.selected_output_names:
#
#             ########################
#             # COMPOSE_PROJECT_NAME #
#             ########################
#
#             yield Output(
#                 output_name="compose_project_name",
#                 value=compose_project_name,
#             )
#
#             yield AssetMaterialization(
#                 asset_key=context.asset_key_for_output("compose_project_name"),
#                 metadata={
#                     "__".join(context.asset_key_for_output("compose_project_name").path): MetadataValue.path(compose_project_name),
#                 },
#             )
#
#         if "cmd_docker_compose_up" in context.selected_output_names:
#
#             #########################
#             # CMD_DOCKER_COMPOSE_UP #
#             #########################
#
#             yield Output(
#                 output_name="cmd_docker_compose_up",
#                 value={
#                     "cmd_docker_compose_up": cmd_docker_compose_up,
#                     "cmd_docker_compose_pull_up": cmd_docker_compose_pull_up,
#                     "cmd_docker_compose_down": cmd_docker_compose_down,
#                     "cmd_docker_compose_logs": cmd_docker_compose_logs,
#                 },
#             )
#
#             yield AssetMaterialization(
#                 asset_key=context.asset_key_for_output("cmd_docker_compose_up"),
#                 metadata={
#                     # "__".join(context.asset_key_for_output("cmd_docker_compose_up").path): MetadataValue.md(
#                     #     f"```shell\n{' '.join(shlex.quote(s) for s in cmd_docker_compose_up)}\n```"
#                     # ),
#                     "cmd_docker_compose_up": MetadataValue.path(
#                         " ".join(
#                             shlex.quote(s) if not s in ["&&", ";"] else s
#                             for s in cmd_docker_compose_up
#                         )
#                     ),
#                     "cmd_docker_compose_pull_up": MetadataValue.path(
#                         " ".join(
#                             shlex.quote(s) if not s in ["&&", ";"] else s
#                             for s in cmd_docker_compose_pull_up
#                         )
#                     ),
#                     "cmd_docker_compose_down": MetadataValue.path(
#                         " ".join(
#                             shlex.quote(s) if not s in ["&&", ";"] else s
#                             for s in cmd_docker_compose_down
#                         )
#                     ),
#                     "cmd_docker_compose_logs": MetadataValue.path(
#                         " ".join(
#                             shlex.quote(s) if not s in ["&&", ";"] else s
#                             for s in cmd_docker_compose_logs
#                         )
#                     ),
#                 },
#             )
#
#     return _op_group_out


@op(
    name="group_out",
    ins={
        "compose": In(dict),
        "group_in": In(dict),
        "cmd_extend": In(list),
        "cmd_append": In(dict[str, list]),
        "CONFIG": In(FeatureBaseModel),
    },
    out={
        "group_out": Out(pathlib.Path),
        "compose_project_name": Out(str),
        "docker_compose_commands": Out(dict[str, list]),
    },
)
def op_group_out(
    context: OpExecutionContext,
    # Todo:
    #  - [ ] remove unused compose (but need to stay here
    #        until done so globally
    #  - [ ] unused because it's just a dependency to make
    #        sure that the compose files actually exist
    #        before compose-graph analyzes them
    compose: dict,  # pylint: disable=redefined-outer-name
    group_in: dict,  # pylint: disable=redefined-outer-name
    cmd_extend: list,  # pylint: disable=redefined-outer-name
    cmd_append: dict[str, list],  # pylint: disable=redefined-outer-name
    CONFIG: FeatureBaseModel,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[pathlib.Path]
    | Output[MutableMapping]
    | Output[str]
    | Output[List]
    | AssetMaterialization,
    None,
    None,
]:

    del compose
    context.log.debug(f"{group_in = }")

    if "group_in" in group_in:
        # Todo:
        #  - [ ] this is a bit hacky
        group_in = group_in["group_in"]

    env: dict = group_in.pop("env")
    docker_config_json: pathlib.Path = group_in.pop("docker_config_json")

    cmd_append["exclude_from_quote"].extend(
        ComposeCmdExclusion.CMD_APPEND_ALWAYS_EXCLUDE_FROM_QUOTATION.value
    )

    DOCKER_COMPOSE: pathlib.Path = CONFIG.docker_compose
    # Todo:
    #  - [ ] Is this necessary here?
    DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

    context.log.debug(context.asset_key_for_output("group_out"))
    context.log.debug(context.asset_key_for_output("compose_project_name"))
    context.log.debug(context.selected_output_names)

    compose_project_name = (
        f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{CONFIG.compose_scope}"
    )

    group_names_by_key_dict = context.assets_def.group_names_by_key
    # Results in:
    # Single Output:
    # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
    # Multiple Outputs:
    # {AssetKey(['Compose_default', 'group_out']): 'Compose_default', AssetKey(['Compose_default', 'compose_project_name']): 'Compose_default'}
    context.log.debug(group_names_by_key_dict)

    cmd_docker_compose_logs = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "logs",
        "--follow",
    ]
    script_cmd_docker_compose_logs = DOCKER_COMPOSE.parent / "docker_compose_logs.sh"

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "up",
        "--remove-orphans",
        # Todo
        #  - [ ] `cmd_extend` seems to have no effect
        #        this can't be intentional...
        *{
            "cmd_extend": cmd_extend,
            "detach": ["--detach"],
            "nothing": [],
        }["detach"],
        *cmd_append["cmd"],
        "&&",
        *cmd_docker_compose_logs,
    ]
    script_cmd_docker_compose_up = DOCKER_COMPOSE.parent / "docker_compose_up.sh"

    cmd_docker_compose_restart = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "restart",
        # "--remove-orphans",
        # Todo
        #  - [ ] `cmd_extend` seems to have no effect
        #        this can't be intentional...
        *{
            "cmd_extend": cmd_extend,
            "detach": ["--detach"],
            "nothing": [],
        }["nothing"],
        # *cmd_append["cmd"],
        # "&&",
        # *cmd_docker_compose_logs,
    ]
    script_cmd_docker_compose_restart = (
        DOCKER_COMPOSE.parent / "docker_compose_restart.sh"
    )

    cmd_docker_compose_pull_up = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "pull",
        "--ignore-pull-failures",
        "&&",
        *cmd_docker_compose_up,
    ]
    script_cmd_docker_compose_pull_up = (
        DOCKER_COMPOSE.parent / "docker_compose_pull_up.sh"
    )

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "down",
        "--remove-orphans",
    ]
    script_cmd_docker_compose_down = DOCKER_COMPOSE.parent / "docker_compose_down.sh"

    # Todo
    #  cmd_docker_exec_it = [
    #      shutil.which("docker"),
    #      "exec",
    #      "--tty",
    #      "--interactive",
    #      "sh",  # or bash
    #  ]
    #  script_cmd_docker_exec_it = DOCKER_COMPOSE.parent / "docker_exec.sh"

    docker_script = dict()
    scripts = []

    docker_script["exe"] = shutil.which("bash")
    docker_script["script"] = str()

    docker_script["script"] += f"#!{docker_script['exe']}\n"
    docker_script[
        "script"
    ] += f"# AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key_for_output('group_out').path)}\n"
    docker_script["script"] += "\n"
    docker_script[
        "script"
    ] += 'SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )\n'
    docker_script["script"] += "\n"

    script_dicts = [
        # A convenience script is a script at the {DOT_LANDSCAPES}/{LANDSCAPE_ID}
        # root that wraps another script.
        {
            "script": script_cmd_docker_compose_up,
            "cmd": cmd_docker_compose_up,
            "create_convenience_script": True,
            # Todo:
            #  - [ ] this is not very elegant (besides, the asset output is
            #        not used anywhere yet:
            #        ```python
            #        if script_dict["create_convenience_script"]:
            #            docker_compose_scope = "__".join(
            #                context.asset_key_for_output(script_dict["asset_key_for_output"]).path
            #            )
            #        ```
            # "asset_key_for_output": "cmd_docker_compose_up",
            "asset_key_for_output": "docker_compose_commands",
        },
        {
            "script": script_cmd_docker_compose_restart,
            "cmd": cmd_docker_compose_restart,
            # Todo
            #  - [ ] "create_convenience_script": True causes the following error (looks like only one can be True):
            # dagster._core.errors.DagsterExecutionStepExecutionError: Error occurred while executing op "group_out_4":
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_plan.py", line 245, in dagster_event_sequence_for_step
            #     yield from check.generator(step_events)
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_step.py", line 501, in core_dagster_event_sequence_for_step
            #     for user_event in _step_output_error_checked_user_event_sequence(
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_step.py", line 184, in _step_output_error_checked_user_event_sequence
            #     for user_event in user_event_sequence:
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_step.py", line 88, in _process_asset_results_to_events
            #     for user_event in user_event_sequence:
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/compute.py", line 190, in execute_core_compute
            #     for step_output in _yield_compute_results(step_context, inputs, compute_fn, compute_context):
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/compute.py", line 159, in _yield_compute_results
            #     for event in iterate_with_context(
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_utils/__init__.py", line 478, in iterate_with_context
            #     with context_fn():
            #   File "/usr/lib/python3.11/contextlib.py", line 158, in __exit__
            #     self.gen.throw(typ, value, traceback)
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/utils.py", line 86, in op_execution_error_boundary
            #     raise error_cls(
            # The above exception was caused by the following exception:
            # dagster._check.functions.CheckError: Failure condition: Output 'cmd_docker_compose_restart' has no asset
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/utils.py", line 56, in op_execution_error_boundary
            #     yield
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_utils/__init__.py", line 480, in iterate_with_context
            #     next_output = next(iterator)
            #                   ^^^^^^^^^^^^^^
            #   File "/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/base/ops/__init__.py", line 1413, in op_group_out
            #     _write_script(script_dict)
            #   File "/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/base/ops/__init__.py", line 1377, in _write_script
            #     context.asset_key_for_output(script_dict["asset_key_for_output"]).path
            #     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/context/op_execution_context.py", line 592, in asset_key_for_output
            #     check.failed(f"Output '{output_name}' has no asset")
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_check/functions.py", line 1696, in failed
            #     raise CheckError(f"Failure condition: {desc}")
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_restart",
        },
        {
            "script": script_cmd_docker_compose_pull_up,
            "cmd": cmd_docker_compose_pull_up,
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_pull_up",
        },
        {
            "script": script_cmd_docker_compose_down,
            "cmd": cmd_docker_compose_down,
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_down",
        },
        {
            "script": script_cmd_docker_compose_logs,
            "cmd": cmd_docker_compose_logs,
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_logs",
        },
    ]

    def _write_script(
        script_dict: dict[str, Union[str, List, pathlib.Path]],
    ):
        """
        This writes the launch scripts that contain the commands to handle Landscapes (up/down etc.).
        If we are not working in Dagster (or the Materializations have been removed, there is
        no other way to reproduce the actual commands other than storing them in these scripts.
        Convenience scripts get created at the root level of a Landscape and point the launch scripts
        themselves. They *should* be portable, hence, the SCRIPT_DIR varible inside the scripts
        is dynamic and, from there, all paths need to be relative to that variable.
        """

        context.log.debug(f"{script_dict = }")

        with open(
            file=script_dict["script"],
            mode="w",
            encoding="utf-8",
        ) as fw:

            context.log.debug(f"Writing script: {script_dict['script'].as_posix()}")

            fw.write(docker_script["script"])
            fw.write("\n")
            fw.write('pushd "${SCRIPT_DIR}" || exit 1\n')
            fw.write("\n")
            fw.write("# Source Overrides defined in {LANDSCAPE}/.overrides\n")
            fw.write('echo "Working Directory: $(pwd)"\n')
            overrides_file = get_relative_path_via_common_root(
                context=context,
                path_src=script_cmd_docker_compose_up,
                path_dst=pathlib.Path(
                    env["DOT_LANDSCAPES"],
                    env.get("LANDSCAPE", "default"),
                    ".overrides",
                ),
                path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
            )
            fw.write(f'echo "Sourcing {overrides_file.as_posix()} file..."\n')
            fw.write(
                f'source {overrides_file.as_posix()} && echo "Sourced successfully." || echo "No .overrides file found."\n'
            )
            fw.write("\n")

            cmd_str = " ".join(
                shlex.quote(s) if not s in cmd_append["exclude_from_quote"] else s
                for s in script_dict["cmd"]
            )

            fw.write(
                f"{cmd_str}\n".replace(
                    # docker-compose.yml
                    DOCKER_COMPOSE.as_posix(),
                    get_relative_path_via_common_root(
                        context=context,
                        path_src=script_cmd_docker_compose_up,
                        path_dst=DOCKER_COMPOSE,
                        path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
                    ).as_posix(),
                ).replace(
                    # OpenStudioLandscapes_Base__docker_config_json
                    pathlib.Path(env["DOT_LANDSCAPES"]).as_posix(),
                    get_relative_path_via_common_root(
                        context=context,
                        path_src=script_cmd_docker_compose_up,
                        path_dst=docker_config_json,
                        path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
                    ).as_posix(),
                )
            )
            fw.write("popd || exit 1\n")
            fw.write("\n")
            fw.write("exit 0;\n")
        os.chmod(
            script_dict["script"],
            mode=os.stat(script_dict["script"]).st_mode | 0o111,
        )

        scripts.append(script_dict["script"].as_posix())

        if script_dict["create_convenience_script"]:
            docker_compose_scope = "__".join(
                context.asset_key_for_output(script_dict["asset_key_for_output"]).path
            )
            script_cmd_convenience = pathlib.Path(
                env["DOT_LANDSCAPES"],
                env.get("LANDSCAPE", "default"),
                f"{docker_compose_scope}.sh",
            )
            rel_path = get_relative_path_via_common_root(
                context=context,
                path_src=script_cmd_convenience,
                path_dst=script_dict["script"],
                path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
            )
            with open(
                file=script_cmd_convenience,
                mode="w",
                encoding="utf-8",
            ) as fw:

                context.log.debug(
                    f"Writing convenience script: {script_cmd_convenience.as_posix()}"
                )

                fw.write(docker_script["script"])
                fw.write("\n")
                fw.write('pushd "${SCRIPT_DIR}" || exit 1\n')
                fw.write(f"{rel_path.as_posix()}\n")
                fw.write("popd || exit 1\n")
                fw.write("\n")
                fw.write("exit 0;\n")
            os.chmod(
                script_cmd_convenience,
                mode=os.stat(script_cmd_convenience).st_mode | 0o111,
            )

    for script_dict in script_dicts:
        _write_script(script_dict)

    if "group_out" in context.selected_output_names:

        # Todo
        #  - [ ] rename to a more descriptive name
        #############
        # GROUP_OUT #
        #############

        yield Output(
            output_name="group_out",
            value=DOCKER_COMPOSE,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("group_out"),
            metadata={
                "__".join(
                    context.asset_key_for_output("group_out").path
                ): MetadataValue.path(DOCKER_COMPOSE),
                "root_dir": MetadataValue.path(DOCKER_COMPOSE.parent),
                # "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
                "scripts": MetadataValue.json(scripts),
            },
        )

    if "compose_project_name" in context.selected_output_names:

        ########################
        # COMPOSE_PROJECT_NAME #
        ########################

        yield Output(
            output_name="compose_project_name",
            value=compose_project_name,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("compose_project_name"),
            metadata={
                "__".join(
                    context.asset_key_for_output("compose_project_name").path
                ): MetadataValue.path(compose_project_name),
            },
        )

    if "docker_compose_commands" in context.selected_output_names:

        ###########################
        # DOCKER_COMPOSE_COMMANDS #
        ###########################

        yield Output(
            output_name="docker_compose_commands",
            value={
                "cmd_docker_compose_up": cmd_docker_compose_up,
                "cmd_docker_compose_restart": cmd_docker_compose_restart,
                "cmd_docker_compose_pull_up": cmd_docker_compose_pull_up,
                "cmd_docker_compose_down": cmd_docker_compose_down,
                "cmd_docker_compose_logs": cmd_docker_compose_logs,
            },
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("docker_compose_commands"),
            metadata={
                "script_cmd_docker_compose_up_down": MetadataValue.path(
                    "; ".join(
                        [
                            script_cmd_docker_compose_up.as_posix(),
                            script_cmd_docker_compose_down.as_posix(),
                        ]
                    )
                ),
                "script_cmd_docker_compose_up": MetadataValue.path(
                    script_cmd_docker_compose_up
                ),
                "script_cmd_docker_compose_restart": MetadataValue.path(
                    script_cmd_docker_compose_restart
                ),
                "script_cmd_docker_compose_pull_up": MetadataValue.path(
                    script_cmd_docker_compose_pull_up
                ),
                "script_cmd_docker_compose_down": MetadataValue.path(
                    script_cmd_docker_compose_down
                ),
                "script_cmd_docker_compose_logs": MetadataValue.path(
                    script_cmd_docker_compose_logs
                ),
            },
        )


@op(
    name="group_out_group_out_compose_scope",
    ins={
        "compose": In(dict),
        "features_in": In(dict),
        "cmd_extend": In(list),
        "cmd_append": In(dict[str, list]),
        "CONFIG": In(ComposeScopeBaseModel),
    },
    out={
        "group_out": Out(pathlib.Path),
        "compose_project_name": Out(str),
        "docker_compose_commands": Out(dict[str, list]),
    },
)
def op_group_out_compose_scope(
    context: OpExecutionContext,
    # Todo:
    #  - [ ] remove unused compose (but need to stay here
    #        until done so globally
    #  - [ ] unused because it's just a dependency to make
    #        sure that the compose files actually exist
    #        before compose-graph analyzes them
    compose: dict,  # pylint: disable=redefined-outer-name
    features_in: dict,  # pylint: disable=redefined-outer-name
    cmd_extend: list,  # pylint: disable=redefined-outer-name
    cmd_append: dict[str, list],  # pylint: disable=redefined-outer-name
    CONFIG: ComposeScopeBaseModel,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[pathlib.Path]
    | Output[MutableMapping]
    | Output[str]
    | Output[List]
    | AssetMaterialization,
    None,
    None,
]:

    del compose

    env: dict = features_in.pop("env_base")
    docker_config_json: pathlib.Path = features_in.pop("docker_config_json")

    cmd_append["exclude_from_quote"].extend(
        ComposeCmdExclusion.CMD_APPEND_ALWAYS_EXCLUDE_FROM_QUOTATION.value
    )

    DOCKER_COMPOSE: pathlib.Path = CONFIG.docker_compose
    # Todo:
    #  - [ ] Is this necessary here?
    DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

    context.log.debug(context.asset_key_for_output("group_out"))
    context.log.debug(context.asset_key_for_output("compose_project_name"))
    context.log.debug(context.selected_output_names)

    compose_project_name = (
        f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{CONFIG.compose_scope}"
    )

    group_names_by_key_dict = context.assets_def.group_names_by_key
    # Results in:
    # Single Output:
    # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
    # Multiple Outputs:
    # {AssetKey(['Compose_default', 'group_out']): 'Compose_default', AssetKey(['Compose_default', 'compose_project_name']): 'Compose_default'}
    context.log.debug(group_names_by_key_dict)

    cmd_docker_compose_logs = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "logs",
        "--follow",
    ]
    script_cmd_docker_compose_logs = DOCKER_COMPOSE.parent / "docker_compose_logs.sh"

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "up",
        "--remove-orphans",
        # Todo
        #  - [ ] `cmd_extend` seems to have no effect
        #        this can't be intentional...
        *{
            "cmd_extend": cmd_extend,
            "detach": ["--detach"],
            "nothing": [],
        }["detach"],
        *cmd_append["cmd"],
        "&&",
        *cmd_docker_compose_logs,
    ]
    script_cmd_docker_compose_up = DOCKER_COMPOSE.parent / "docker_compose_up.sh"

    cmd_docker_compose_restart = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "restart",
        # "--remove-orphans",
        # Todo
        #  - [ ] `cmd_extend` seems to have no effect
        #        this can't be intentional...
        *{
            "cmd_extend": cmd_extend,
            "detach": ["--detach"],
            "nothing": [],
        }["nothing"],
        # *cmd_append["cmd"],
        # "&&",
        # *cmd_docker_compose_logs,
    ]
    script_cmd_docker_compose_restart = (
        DOCKER_COMPOSE.parent / "docker_compose_restart.sh"
    )

    cmd_docker_compose_pull_up = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "pull",
        "--ignore-pull-failures",
        "&&",
        *cmd_docker_compose_up,
    ]
    script_cmd_docker_compose_pull_up = (
        DOCKER_COMPOSE.parent / "docker_compose_pull_up.sh"
    )

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "--config",
        docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "down",
        "--remove-orphans",
    ]
    script_cmd_docker_compose_down = DOCKER_COMPOSE.parent / "docker_compose_down.sh"

    # Todo
    #  cmd_docker_exec_it = [
    #      shutil.which("docker"),
    #      "exec",
    #      "--tty",
    #      "--interactive",
    #      "sh",  # or bash
    #  ]
    #  script_cmd_docker_exec_it = DOCKER_COMPOSE.parent / "docker_exec.sh"

    docker_script = dict()
    scripts = []

    docker_script["exe"] = shutil.which("bash")
    docker_script["script"] = str()

    docker_script["script"] += f"#!{docker_script['exe']}\n"
    docker_script[
        "script"
    ] += f"# AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key_for_output('group_out').path)}\n"
    docker_script["script"] += "\n"
    docker_script[
        "script"
    ] += 'SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )\n'
    docker_script["script"] += "\n"

    script_dicts = [
        # A convenience script is a script at the {DOT_LANDSCAPES}/{LANDSCAPE_ID}
        # root that wraps another script.
        {
            "script": script_cmd_docker_compose_up,
            "cmd": cmd_docker_compose_up,
            "create_convenience_script": True,
            # Todo:
            #  - [ ] this is not very elegant (besides, the asset output is
            #        not used anywhere yet:
            #        ```python
            #        if script_dict["create_convenience_script"]:
            #            docker_compose_scope = "__".join(
            #                context.asset_key_for_output(script_dict["asset_key_for_output"]).path
            #            )
            #        ```
            # "asset_key_for_output": "cmd_docker_compose_up",
            "asset_key_for_output": "docker_compose_commands",
        },
        {
            "script": script_cmd_docker_compose_restart,
            "cmd": cmd_docker_compose_restart,
            # Todo
            #  - [ ] "create_convenience_script": True causes the following error (looks like only one can be True):
            # dagster._core.errors.DagsterExecutionStepExecutionError: Error occurred while executing op "group_out_4":
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_plan.py", line 245, in dagster_event_sequence_for_step
            #     yield from check.generator(step_events)
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_step.py", line 501, in core_dagster_event_sequence_for_step
            #     for user_event in _step_output_error_checked_user_event_sequence(
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_step.py", line 184, in _step_output_error_checked_user_event_sequence
            #     for user_event in user_event_sequence:
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/execute_step.py", line 88, in _process_asset_results_to_events
            #     for user_event in user_event_sequence:
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/compute.py", line 190, in execute_core_compute
            #     for step_output in _yield_compute_results(step_context, inputs, compute_fn, compute_context):
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/compute.py", line 159, in _yield_compute_results
            #     for event in iterate_with_context(
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_utils/__init__.py", line 478, in iterate_with_context
            #     with context_fn():
            #   File "/usr/lib/python3.11/contextlib.py", line 158, in __exit__
            #     self.gen.throw(typ, value, traceback)
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/utils.py", line 86, in op_execution_error_boundary
            #     raise error_cls(
            # The above exception was caused by the following exception:
            # dagster._check.functions.CheckError: Failure condition: Output 'cmd_docker_compose_restart' has no asset
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/plan/utils.py", line 56, in op_execution_error_boundary
            #     yield
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_utils/__init__.py", line 480, in iterate_with_context
            #     next_output = next(iterator)
            #                   ^^^^^^^^^^^^^^
            #   File "/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/base/ops/__init__.py", line 1413, in op_group_out
            #     _write_script(script_dict)
            #   File "/home/michael/git/repos/OpenStudioLandscapes/src/OpenStudioLandscapes/engine/base/ops/__init__.py", line 1377, in _write_script
            #     context.asset_key_for_output(script_dict["asset_key_for_output"]).path
            #     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_core/execution/context/op_execution_context.py", line 592, in asset_key_for_output
            #     check.failed(f"Output '{output_name}' has no asset")
            #   File "/home/michael/git/repos/OpenStudioLandscapes/.venv/lib/python3.11/site-packages/dagster/_check/functions.py", line 1696, in failed
            #     raise CheckError(f"Failure condition: {desc}")
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_restart",
        },
        {
            "script": script_cmd_docker_compose_pull_up,
            "cmd": cmd_docker_compose_pull_up,
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_pull_up",
        },
        {
            "script": script_cmd_docker_compose_down,
            "cmd": cmd_docker_compose_down,
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_down",
        },
        {
            "script": script_cmd_docker_compose_logs,
            "cmd": cmd_docker_compose_logs,
            "create_convenience_script": False,
            "asset_key_for_output": "cmd_docker_compose_logs",
        },
    ]

    def _write_script(
        script_dict: dict[str, Union[str, List, pathlib.Path]],
    ):
        """
        This writes the launch scripts that contain the commands to handle Landscapes (up/down etc.).
        If we are not working in Dagster (or the Materializations have been removed, there is
        no other way to reproduce the actual commands other than storing them in these scripts.
        Convenience scripts get created at the root level of a Landscape and point the launch scripts
        themselves. They *should* be portable, hence, the SCRIPT_DIR varible inside the scripts
        is dynamic and, from there, all paths need to be relative to that variable.
        """

        context.log.debug(f"{script_dict = }")

        with open(
            file=script_dict["script"],
            mode="w",
            encoding="utf-8",
        ) as fw:

            context.log.debug(f"Writing script: {script_dict['script'].as_posix()}")

            fw.write(docker_script["script"])
            fw.write("\n")
            fw.write('pushd "${SCRIPT_DIR}" || exit 1\n')
            fw.write("\n")
            fw.write("# Source Overrides defined in {LANDSCAPE}/.overrides\n")
            fw.write('echo "Working Directory: $(pwd)"\n')
            overrides_file = get_relative_path_via_common_root(
                context=context,
                path_src=script_cmd_docker_compose_up,
                path_dst=pathlib.Path(
                    env["DOT_LANDSCAPES"],
                    env.get("LANDSCAPE", "default"),
                    ".overrides",
                ),
                path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
            )
            fw.write(f'echo "Sourcing {overrides_file.as_posix()} file..."\n')
            fw.write(
                f'source {overrides_file.as_posix()} && echo "Sourced successfully." || echo "No .overrides file found."\n'
            )
            fw.write("\n")

            cmd_str = " ".join(
                shlex.quote(s) if not s in cmd_append["exclude_from_quote"] else s
                for s in script_dict["cmd"]
            )

            fw.write(
                f"{cmd_str}\n".replace(
                    # docker-compose.yml
                    DOCKER_COMPOSE.as_posix(),
                    get_relative_path_via_common_root(
                        context=context,
                        path_src=script_cmd_docker_compose_up,
                        path_dst=DOCKER_COMPOSE,
                        path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
                    ).as_posix(),
                ).replace(
                    # OpenStudioLandscapes_Base__docker_config_json
                    pathlib.Path(env["DOT_LANDSCAPES"]).as_posix(),
                    get_relative_path_via_common_root(
                        context=context,
                        path_src=script_cmd_docker_compose_up,
                        path_dst=docker_config_json,
                        path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
                    ).as_posix(),
                )
            )
            fw.write("popd || exit 1\n")
            fw.write("\n")
            fw.write("exit 0;\n")
        os.chmod(
            script_dict["script"],
            mode=os.stat(script_dict["script"]).st_mode | 0o111,
        )

        scripts.append(script_dict["script"].as_posix())

        if script_dict["create_convenience_script"]:
            docker_compose_scope = "__".join(
                context.asset_key_for_output(script_dict["asset_key_for_output"]).path
            )
            script_cmd_convenience = pathlib.Path(
                env["DOT_LANDSCAPES"],
                env.get("LANDSCAPE", "default"),
                f"{docker_compose_scope}.sh",
            )
            rel_path = get_relative_path_via_common_root(
                context=context,
                path_src=script_cmd_convenience,
                path_dst=script_dict["script"],
                path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
            )
            with open(
                file=script_cmd_convenience,
                mode="w",
                encoding="utf-8",
            ) as fw:

                context.log.debug(
                    f"Writing convenience script: {script_cmd_convenience.as_posix()}"
                )

                fw.write(docker_script["script"])
                fw.write("\n")
                fw.write('pushd "${SCRIPT_DIR}" || exit 1\n')
                fw.write(f"{rel_path.as_posix()}\n")
                fw.write("popd || exit 1\n")
                fw.write("\n")
                fw.write("exit 0;\n")
            os.chmod(
                script_cmd_convenience,
                mode=os.stat(script_cmd_convenience).st_mode | 0o111,
            )

    for script_dict in script_dicts:
        _write_script(script_dict)

    if "group_out" in context.selected_output_names:

        # Todo
        #  - [ ] rename to a more descriptive name
        #############
        # GROUP_OUT #
        #############

        yield Output(
            output_name="group_out",
            value=DOCKER_COMPOSE,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("group_out"),
            metadata={
                "__".join(
                    context.asset_key_for_output("group_out").path
                ): MetadataValue.path(DOCKER_COMPOSE),
                "root_dir": MetadataValue.path(DOCKER_COMPOSE.parent),
                # "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
                "scripts": MetadataValue.json(scripts),
            },
        )

    if "compose_project_name" in context.selected_output_names:

        ########################
        # COMPOSE_PROJECT_NAME #
        ########################

        yield Output(
            output_name="compose_project_name",
            value=compose_project_name,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("compose_project_name"),
            metadata={
                "__".join(
                    context.asset_key_for_output("compose_project_name").path
                ): MetadataValue.path(compose_project_name),
            },
        )

    if "docker_compose_commands" in context.selected_output_names:

        ###########################
        # DOCKER_COMPOSE_COMMANDS #
        ###########################

        yield Output(
            output_name="docker_compose_commands",
            value={
                "cmd_docker_compose_up": cmd_docker_compose_up,
                "cmd_docker_compose_restart": cmd_docker_compose_restart,
                "cmd_docker_compose_pull_up": cmd_docker_compose_pull_up,
                "cmd_docker_compose_down": cmd_docker_compose_down,
                "cmd_docker_compose_logs": cmd_docker_compose_logs,
            },
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("docker_compose_commands"),
            metadata={
                "script_cmd_docker_compose_up_down": MetadataValue.path(
                    "; ".join(
                        [
                            script_cmd_docker_compose_up.as_posix(),
                            script_cmd_docker_compose_down.as_posix(),
                        ]
                    )
                ),
                "script_cmd_docker_compose_up": MetadataValue.path(
                    script_cmd_docker_compose_up
                ),
                "script_cmd_docker_compose_restart": MetadataValue.path(
                    script_cmd_docker_compose_restart
                ),
                "script_cmd_docker_compose_pull_up": MetadataValue.path(
                    script_cmd_docker_compose_pull_up
                ),
                "script_cmd_docker_compose_down": MetadataValue.path(
                    script_cmd_docker_compose_down
                ),
                "script_cmd_docker_compose_logs": MetadataValue.path(
                    script_cmd_docker_compose_logs
                ),
            },
        )
