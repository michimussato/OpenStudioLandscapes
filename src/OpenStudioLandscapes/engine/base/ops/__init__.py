__all__ = [
    "factory_feature_out",
    "factory_feature_in",
    "op_compose",
    "op_group_in",
    "op_group_out",
    "op_env",
    "op_constants",
    "op_docker_compose_graph",
]

import base64
import copy
import os
import pathlib
import shlex
import shutil
from collections import ChainMap
from functools import reduce
from typing import Generator, MutableMapping, Any

import yaml
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
    OpDefinition,
)

from docker_compose_graph.docker_compose_graph import DockerComposeGraph

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *


def factory_feature_out(
    name="op_feature_out_from_factory",
    ins=None,
    **kwargs,
) -> OpDefinition:
    """
    https://docs.dagster.io/guides/build/ops#op-factory

    Args:
        name (str): The name of the new op.
        ins (Dict[str, In]): Any Ins for the new op. Default: None.

    Returns:
        function: The new op.
    """

    @op(
        name=name,
        ins=ins,
        **kwargs,
    )
    def _op_feature_out(
        context: OpExecutionContext,
        **kwargs,
    ):

        metadata = {}

        # I want
        # - env_base
        # - constants_base
        # - features
        # - docker_config
        # to stay in the root level
        # of the dict
        env_base = kwargs["group_in"].pop("env_base")
        kwargs["env_base"] = env_base
        constants_base = kwargs["group_in"].pop("constants_base")
        kwargs["constants_base"] = constants_base
        features = kwargs["group_in"].pop("features")
        kwargs["features"] = features
        docker_config = kwargs["group_in"].pop("docker_config")
        kwargs["docker_config"] = docker_config

        # Todo
        #  - [ ] replace "group_out" (i.e. with "compose_yaml" or "feature_out")
        kwargs["compose_yaml"] = kwargs["env"]["DOCKER_COMPOSE"]

        out_ = copy.deepcopy(kwargs)

        # JSON cannot serialize certain types
        # out of the box. This makes sure that
        # MetadataValue.json receives only
        # serializable input.
        def _serialize(d):
            for k_, v_ in d.items():
                if isinstance(v_, dict):
                    _serialize(v_)
                elif isinstance(v_, pathlib.PosixPath):
                    d[k_] = v_.as_posix()
                else:
                    d[k_] = str(v_)

        _serialize(out_)

        for k, v in out_.items():
            context.log.warning(k)
            context.log.warning(v)
            metadata[k] = MetadataValue.json(v)

        yield Output(
            output_name="feature_out",
            value=kwargs,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("feature_out"),
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(out_),
                **metadata,
            },
        )

    return _op_feature_out


def factory_feature_in(
    name="op_feature_in_from_factory",
    ins=None,
    **kwargs,
) -> OpDefinition:
    """
    https://docs.dagster.io/guides/build/ops#op-factory

    Args:
        name (str): The name of the new op.
        ins (Dict[str, In]): Any Ins for the new op. Default: None.

    Returns:
        function: The new op.
    """

    @op(
        name=name,
        ins=ins,
        **kwargs,
    )
    def _op_feature_in(
        context: OpExecutionContext,
        **kwargs,
    ):

        # out = {}
        metadata = {}

        # for k, v in kwargs.items():
        #     if k == "group_in":
        #         v = {k: v}
        #     out[k] = v

        out_ = copy.deepcopy(kwargs)

        # JSON cannot serialize certain types
        # out of the box. This makes sure that
        # MetadataValue.json receives only
        # serializable input.
        def _serialize(d):
            for k_, v_ in d.items():
                if isinstance(v_, dict):
                    _serialize(v_)
                elif isinstance(v_, pathlib.PosixPath):
                    d[k_] = v_.as_posix()
                else:
                    d[k_] = str(v_)

        _serialize(out_)

        for k, v in out_.items():
            context.log.warning(k)
            context.log.warning(v)
            metadata[k] = MetadataValue.json(v)

        yield Output(
            output_name="feature_out",
            value=kwargs,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("feature_out"),
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(out_),
                **metadata,
            },
        )

    return _op_feature_in


@op(
    name="compose",
    ins={
        "compose_networks": In(dict),
        "compose_maps": In(list),
        "env": In(dict),
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
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
    DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

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

    # Write docker-compose.yaml
    with open(DOCKER_COMPOSE, mode="w", encoding="utf-8") as fw:
        fw.write(docker_yaml)

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
    name="op_group_in",
    ins={
        "group_out": In(dict),
    },
    out={
        "group_in": Out(dict),
    },
)
def op_group_in(
    context: OpExecutionContext,
    group_out: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """
    This is the entry point for a Feature.
    Just forwards the data we get from the upstream `group_out` asset.
    """

    context.log.debug(group_out)

    yield Output(
        output_name="group_in",
        value=group_out,
    )

    metadata = {}

    for k, v in group_out.items():
        try:
            metadata[k] = MetadataValue.json(v)
        except Exception:
            # This is for Non-JSON-Serializable Objects.
            # Even though a DagsterExecutionStepExecutionError is thrown,
            # it cannot not be captured here for some reason. Hence, Exception
            metadata[v.name] = MetadataValue.json(v.value)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata=metadata,
    )


# @op(
#     name="op_group_in",
#     ins={
#         "group_out": In(dict),
#     },
#     out={
#         "group_in": Out(dict),
#     },
# )
# def op_feature_in(
#     context: OpExecutionContext,
#     group_out: dict,  # pylint: disable=redefined-outer-name
# ) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
#     """
#     This is the entry point for a Feature.
#     Just forwards the data we get from the upstream `group_out` asset.
#     """
#
#     context.log.debug(group_out)
#
#     yield Output(
#         output_name="group_in",
#         value=group_out,
#     )
#
#     metadata = {}
#
#     for k, v in group_out.items():
#         try:
#             metadata[k] = MetadataValue.json(v)
#         except Exception:
#             # This is for Non-JSON-Serializable Objects.
#             # Even though a DagsterExecutionStepExecutionError is thrown,
#             # it cannot not be captured here for some reason. Hence, Exception
#             metadata[v.name] = MetadataValue.json(v.value)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata=metadata,
#     )


@op(
    name="op_env",
    ins={
        "group_in": In(dict),
        "constants": In(dict),
        "FEATURE_CONFIG": In(OpenStudioLandscapesConfig),
        "COMPOSE_SCOPE": In(ComposeScope),
        "DOCKER_COMPOSE": In(pathlib.Path),
    },
    out={
        "env_out": Out(dict),
    },
)
def op_env(
    context: OpExecutionContext,
    group_in: dict,  # pylint: disable=redefined-outer-name
    constants: dict,  # pylint: disable=redefined-outer-name
    FEATURE_CONFIG: OpenStudioLandscapesConfig,  # pylint: disable=redefined-outer-name
    COMPOSE_SCOPE: ComposeScope,  # pylint: disable=redefined-outer-name
    DOCKER_COMPOSE: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
    """
    Provides a Feature with the `env` dict.
    """

    env_in = copy.deepcopy(group_in["env"])

    env_in.update(
        expand_dict_vars(
            dict_to_expand={
                "DOCKER_COMPOSE": DOCKER_COMPOSE.as_posix()
            },
            kv=env_in,
        )
    )

    env_in.update(
        expand_dict_vars(
            dict_to_expand=constants[FEATURE_CONFIG],
            kv=env_in,
        )
    )

    env_in.update(
        {
            "COMPOSE_SCOPE": COMPOSE_SCOPE,
        },
    )

    yield Output(
        output_name="env_out",
        value=env_in,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_in),
            "ENVIRONMENT": MetadataValue.json(constants[FEATURE_CONFIG]),
        },
    )


@op(
    name="op_constants",
    ins={
        "group_in": In(dict),
        "NAME": In(str),
    },
    out={
        "COMPOSE_SCOPE": Out(ComposeScope),
        "FEATURE_CONFIG": Out(OpenStudioLandscapesConfig),
        # "FEATURE_CONFIGS": Out(dict),
        # "DOCKER_USE_CACHE": Out(bool),
    },
)
def op_constants(
    context: OpExecutionContext,
    group_in: dict,  # pylint: disable=redefined-outer-name
    NAME: str,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[ComposeScope]
    | AssetMaterialization
    | Output[Any]
    | Output[dict[OpenStudioLandscapesConfig, dict[str, bool | str | Any]]]
    | Output[bool | Any]
    | Any,
    None,
    None,
]:
    """
    Provides a Feature with some constant data.
    """

    features = group_in["features"]

    # COMPOSE_SCOPE
    COMPOSE_SCOPE = get_compose_scope(
        context=context,
        features=features,
        name=NAME,
    )

    # FEATURE_CONFIG
    FEATURE_CONFIG = get_feature_config(
        context=context,
        features=features,
        name=NAME,
    )

    yield Output(
        output_name="COMPOSE_SCOPE",
        value=COMPOSE_SCOPE,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("COMPOSE_SCOPE"),
        metadata={
            "__".join(
                context.asset_key_for_output("COMPOSE_SCOPE").path
            ): MetadataValue.json(COMPOSE_SCOPE),
        },
    )

    yield Output(
        output_name="FEATURE_CONFIG",
        value=FEATURE_CONFIG,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("FEATURE_CONFIG"),
        metadata={
            "__".join(
                context.asset_key_for_output("FEATURE_CONFIG").path
            ): MetadataValue.json(FEATURE_CONFIG),
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
        "docker_compose_graph_dot": Out(pathlib.Path),
    },
)
def op_docker_compose_graph(
    context: OpExecutionContext,
    group_out: pathlib.Path,  # pylint: disable=redefined-outer-name
    compose_project_name: str,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pydot.Dot] | Output[pathlib.Path] | AssetMaterialization, None, None]:
    """ """

    dcg = DockerComposeGraph(
        label_root_service=compose_project_name,
    )
    trees = dcg.parse_docker_compose(pathlib.Path(group_out))

    context.log.info(trees)

    dcg.iterate_trees(trees)

    docker_compose_dir = group_out.parent / "__".join(context.asset_key_for_output("docker_compose_graph").path)

    docker_compose_dir.mkdir(parents=True, exist_ok=True)

    # SVG
    svg = docker_compose_dir / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.svg"
    dcg.graph.write(
        path=svg,
        format="svg",
    )

    with open(svg, "rb") as fr:
        svg_bytes = fr.read()

    svg_base64 = base64.b64encode(svg_bytes).decode("utf-8")
    svg_md = f"![Image](data:image/svg+xml;base64,{svg_base64})"

    # PNG
    png = docker_compose_dir / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.png"
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
    dot = docker_compose_dir / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.dot"
    dcg.graph.write(
        path=dot,
        format="dot",
    )

    if "docker_compose_graph" in context.selected_output_names:

        ########################
        # DOCKER_COMPOSE_GRAPH #
        ########################

        yield Output(
            output_name="docker_compose_graph",
            value=dcg.graph,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("docker_compose_graph"),
            metadata={
                "svg": MetadataValue.md(svg_md),
                "__".join(context.asset_key_for_output("docker_compose_graph").path): MetadataValue.json(str(dcg.graph)),
                "svg_path": MetadataValue.path(svg),
                "png_path": MetadataValue.path(png),
            },
        )

    if "docker_compose_graph_dot" in context.selected_output_names:

        ############################
        # DOCKER_COMPOSE_GRAPH_DOT #
        ############################

        yield Output(
            output_name="docker_compose_graph_dot",
            value=dot,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("docker_compose_graph_dot"),
            metadata={
                "__".join(context.asset_key_for_output("docker_compose_graph_dot").path): MetadataValue.path(dot),
            },
        )


@op(
    name="group_out",
    ins={
        "compose": In(dict),
        "env": In(dict),
        # "group_in": In(dict),
        "docker_config": In(DockerConfig),
    },
    out={
        "group_out": Out(pathlib.Path),
        "compose_project_name": Out(str),
        "cmd_docker_compose_up": Out(dict[str, list]),
    },
)
def op_group_out(
    context: OpExecutionContext,
    compose: dict,  # pylint: disable=redefined-outer-name
    env: dict,  # pylint: disable=redefined-outer-name
    # group_in: dict,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | Output[dict] | Output[str] | Output[list] | AssetMaterialization, None, None]:

    DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])

    context.log.debug(context.asset_key_for_output("group_out"))
    context.log.debug(context.asset_key_for_output("compose_project_name"))
    context.log.debug(context.selected_output_names)

    build_base_docker_config: DockerConfig = docker_config
    build_base_docker_config_value = build_base_docker_config.value

    compose_project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{env['COMPOSE_SCOPE']}"

    group_names_by_key_dict = (
        context.assets_def.group_names_by_key
    )
    # Results in:
    # Single Output:
    # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
    # Multiple Outputs:
    # {AssetKey(['Compose_default', 'group_out']): 'Compose_default', AssetKey(['Compose_default', 'compose_project_name']): 'Compose_default'}
    context.log.debug(group_names_by_key_dict)

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "up",
        "--remove-orphans",
    ]
    script_cmd_docker_compose_up = DOCKER_COMPOSE.parent / "docker_compose_up.sh"

    cmd_docker_compose_logs = [
        shutil.which("docker"),
        "compose",
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "logs",
        "--follow",
    ]
    script_cmd_docker_compose_logs = DOCKER_COMPOSE.parent / "docker_compose_logs.sh"

    cmd_docker_compose_pull_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        DOCKER_COMPOSE.as_posix(),
        "--project-name",
        compose_project_name,
        "pull",
        "--ignore-pull-failures",
        "&&",
        *cmd_docker_compose_up,
    ]
    script_cmd_docker_compose_pull_up = DOCKER_COMPOSE.parent / "docker_compose_pull_up.sh"

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "compose",
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

    # In case we need to log in to the registry
    if not build_base_docker_config_value["docker_use_local"]:

        if build_base_docker_config_value["docker_repository_type"] == DockerRepositoryType.PRIVATE:

            server = build_base_docker_config_value["docker_registry_url"]
            username = build_base_docker_config_value.get("docker_registry_username", None)
            password = build_base_docker_config_value.get("docker_registry_password", None)

            if not all([username, password]):
                raise Exception("Both username and password are required")

            cmd_docker_login = [
                shutil.which("docker"),
                "login",
                "--username", username,
                "--password", password,
                server,
            ]

            cmd_docker_logout = [
                shutil.which("docker"),
                "logout",
            ]

            cmd_docker_compose_up = [
                *cmd_docker_login,
                "&&",
                *cmd_docker_compose_up,
                "&&",
                *cmd_docker_logout,
            ]

            cmd_docker_compose_pull_up =  [
                *cmd_docker_login,
                "&&",
                *cmd_docker_compose_pull_up,
                "&&",
                *cmd_docker_logout,
            ]

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
        fw.write(f"{shlex.join(cmd_docker_compose_up)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
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
        fw.write(f"{shlex.join(cmd_docker_compose_pull_up)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
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
        fw.write(f"{shlex.join(cmd_docker_compose_down)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
        fw.write("\n")
        fw.write("exit 0;\n")
    os.chmod(
        script_cmd_docker_compose_down,
        mode=os.stat(script_cmd_docker_compose_down).st_mode | 0o111,
    )
    scripts.append(script_cmd_docker_compose_down.as_posix())

    with open(
        file=script_cmd_docker_compose_logs,
        mode="w",
        encoding="utf-8",
    ) as fw:
        fw.write(docker_script["script"])
        fw.write(f"{shlex.join(cmd_docker_compose_logs)}\n".replace(DOCKER_COMPOSE.parent.as_posix(), '"${SCRIPT_DIR}"'))
        fw.write("\n")
        fw.write("exit 0;\n")
    os.chmod(
        script_cmd_docker_compose_logs,
        mode=os.stat(script_cmd_docker_compose_logs).st_mode | 0o111,
    )
    scripts.append(script_cmd_docker_compose_logs.as_posix())

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
                "__".join(context.asset_key_for_output("group_out").path): MetadataValue.path(DOCKER_COMPOSE),
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
                "__".join(context.asset_key_for_output("compose_project_name").path): MetadataValue.path(compose_project_name),
            },
        )

    if "cmd_docker_compose_up" in context.selected_output_names:

        #########################
        # CMD_DOCKER_COMPOSE_UP #
        #########################

        yield Output(
            output_name="cmd_docker_compose_up",
            value={
                "cmd_docker_compose_up": cmd_docker_compose_up,
                "cmd_docker_compose_pull_up": cmd_docker_compose_pull_up,
                "cmd_docker_compose_down": cmd_docker_compose_down,
                "cmd_docker_compose_logs": cmd_docker_compose_logs,
            },
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output("cmd_docker_compose_up"),
            metadata={
                # "__".join(context.asset_key_for_output("cmd_docker_compose_up").path): MetadataValue.md(
                #     f"```shell\n{' '.join(shlex.quote(s) for s in cmd_docker_compose_up)}\n```"
                # ),
                "cmd_docker_compose_up": MetadataValue.path(
                    " ".join(
                        shlex.quote(s) if not s in ["&&", ";"] else s
                        for s in cmd_docker_compose_up
                    )
                ),
                "cmd_docker_compose_pull_up": MetadataValue.path(
                    " ".join(
                        shlex.quote(s) if not s in ["&&", ";"] else s
                        for s in cmd_docker_compose_pull_up
                    )
                ),
                "cmd_docker_compose_down": MetadataValue.path(
                    " ".join(
                        shlex.quote(s) if not s in ["&&", ";"] else s
                        for s in cmd_docker_compose_down
                    )
                ),
                "cmd_docker_compose_logs": MetadataValue.path(
                    " ".join(
                        shlex.quote(s) if not s in ["&&", ";"] else s
                        for s in cmd_docker_compose_logs
                    )
                ),
            },
        )
