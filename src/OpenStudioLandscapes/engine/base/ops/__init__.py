__all__ = [
    "factory_feature_out",
    "factory_feature_in",
    "factory_docker_config",
    "factory_compose",
    "factory_group_in",
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
from typing import Generator, MutableMapping, Any, List

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
from OpenStudioLandscapes.engine.constants import *


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

        # I want
        # - env_base
        # - constants_base
        # - features
        # - docker_config
        # - docker_config_json
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
        docker_config_json = kwargs["group_in"].pop("docker_config_json")
        kwargs["docker_config_json"] = docker_config_json

        # Todo
        #  - [ ] replace "group_out" (i.e. with "compose_yaml" or "feature_out")
        kwargs["compose_yaml"] = kwargs["env"]["DOCKER_COMPOSE"]

        output_name = "feature_out"

        yield Output(
            output_name=output_name,
            value=kwargs,
        )

        kwargs_serialized = copy.deepcopy(kwargs)

        serialize_dict(
            context=context,
            d=kwargs_serialized,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(kwargs_serialized),
                **metadatavalues_from_dict(
                    context=context,
                    d_serialized=kwargs_serialized,
                ),
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

        output_name = "feature_out"

        yield Output(
            output_name=output_name,
            value=kwargs,
        )

        kwargs_serialized = copy.deepcopy(kwargs)

        serialize_dict(
            context=context,
            d=kwargs_serialized,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(kwargs_serialized),
                **metadatavalues_from_dict(
                    context=context,
                    d_serialized=kwargs_serialized,
                ),
            },
        )

    return _op_feature_in


def factory_docker_config(
    name="op_docker_config_from_factory",
    ins=None,
    # out=None,
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
    def _op_docker_config(
        context: OpExecutionContext,
        **kwargs,
    ):

        group_in = kwargs.pop("group_in")
        context.log.debug(group_in)
        docker_config: DockerConfig = group_in.pop("docker_config")
        context.log.debug(docker_config)

        output_name = "docker_config"

        yield Output(
            output_name=output_name,
            value=docker_config,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                docker_config.name: MetadataValue.json(docker_config.value),
            },
        )

    return _op_docker_config


# def factory_docker_config_json(
#     name="op_docker_config_json_from_factory",
#     ins=None,
#     # out=None,
#     **kwargs,
# ) -> OpDefinition:
#     """
#     https://docs.dagster.io/guides/build/ops#op-factory
#
#     Args:
#         name (str): The name of the new op.
#         ins (Dict[str, In]): Any Ins for the new op. Default: None.
#
#     Returns:
#         function: The new op.
#     """
#
#     @op(
#         name=name,
#         ins=ins,
#         **kwargs,
#     )
#     def _op_docker_config_json(
#         context: OpExecutionContext,
#         **kwargs,
#     ):
#
#         group_in = kwargs.pop("group_in")
#         context.log.debug(group_in)
#         docker_config: DockerConfig = group_in.pop("docker_config")
#         context.log.debug(docker_config)
#
#         output_name = "docker_config_json"
#
#         yield Output(
#             output_name=output_name,
#             value=docker_config,
#         )
#
#         yield AssetMaterialization(
#             asset_key=context.asset_key_for_output(output_name),
#             metadata={
#                 docker_config.name: MetadataValue.json(docker_config.value),
#             },
#         )
#
#     return _op_docker_config_json


def factory_compose(
    name="op_compose_from_factory",
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
    def _op_compose(
        context: OpExecutionContext,
        **kwargs,
    ):
        """ """

        env = kwargs.pop("env")
        compose_networks = kwargs.pop("compose_networks")
        compose_maps = kwargs.pop("compose_maps")

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

    return _op_compose


def factory_group_in(
    name="op_group_in_factory",
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
    def _op_group_in(
        context: OpExecutionContext,
        **kwargs,
    ):
        """
        This is the entry point for a Feature.
        Just forwards the data we get from the upstream `group_out` asset.
        """

        kw_keys = list(kwargs.keys())

        context.log.debug(f"{kw_keys = }")

        # We expect an enums.GroupIn value here
        # Make sure there is only one key
        if len(kw_keys) == 1:
            kw_key = kw_keys[0]
        else:
            raise NotImplementedError()
        # Access Enum value by key:
        # https://stackoverflow.com/a/38716384
        group_out = kwargs.pop(GroupIn(kw_key))

        context.log.debug(f"{group_out = }")

        yield Output(
            output_name="group_in",
            value=group_out,
        )

        group_out_serialized = copy.deepcopy(group_out)

        serialize_dict(
            context=context,
            d=group_out_serialized,
        )

        context.log.debug(f"{group_out_serialized = }")

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata=metadatavalues_from_dict(
                context=context,
                d_serialized=group_out_serialized,
            ),
        )

    return _op_group_in


# Todo
#  - [ ] convert to factory
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


# Todo
#  - [ ] convert to factory
@op(
    name="op_docker_config_json",
    ins={
        "group_in": In(dict),
        # "constants": In(dict),
        # "FEATURE_CONFIG": In(OpenStudioLandscapesConfig),
        # "COMPOSE_SCOPE": In(ComposeScope),
        # "DOCKER_COMPOSE": In(pathlib.Path),
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
    name="op_constants",
    ins={
        "group_in": In(dict),
        "NAME": In(str),
    },
    out={
        "COMPOSE_SCOPE": Out(ComposeScope),
        "FEATURE_CONFIG": Out(OpenStudioLandscapesConfig),
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
    | Output[MutableMapping[OpenStudioLandscapesConfig, MutableMapping[str, bool | str | Any]]]
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
    png = docker_compose_dir / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.png"
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
    dot = docker_compose_dir / f"{'__'.join(context.asset_key_for_output('docker_compose_graph').path)}.dot"
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
            "__".join(context.asset_key_for_output("docker_compose_graph").path): MetadataValue.json(str(dcg.graph)),
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
            "__".join(context.asset_key_for_output("docker_compose_graph_dot").path): MetadataValue.path(dot),
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
        "env": In(dict),
        "docker_config": In(DockerConfig),
        "docker_config_json": In(pathlib.Path),
    },
    out={
        "group_out": Out(pathlib.Path),
        "compose_project_name": Out(str),
        "cmd_docker_compose_up": Out(dict[str, list]),
    },
)
def op_group_out(
    context: OpExecutionContext,
    # Todo:
    #  - [ ] remove unused compose
    compose: dict,  # pylint: disable=redefined-outer-name
    env: dict,  # pylint: disable=redefined-outer-name
    # group_in: dict,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | Output[MutableMapping] | Output[str] | Output[List] | AssetMaterialization, None, None]:

    DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
    # Todo:
    #  - [ ] Is this necessary here?
    DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

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
        "--config", docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file",  DOCKER_COMPOSE.as_posix(),
        "--project-name", compose_project_name,
        "up",
        "--remove-orphans",
    ]
    script_cmd_docker_compose_up = DOCKER_COMPOSE.parent / "docker_compose_up.sh"

    cmd_docker_compose_logs = [
        shutil.which("docker"),
        "--config", docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file", DOCKER_COMPOSE.as_posix(),
        "--project-name", compose_project_name,
        "logs",
        "--follow",
    ]
    script_cmd_docker_compose_logs = DOCKER_COMPOSE.parent / "docker_compose_logs.sh"

    cmd_docker_compose_pull_up = [
        shutil.which("docker"),
        "--config", docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file", DOCKER_COMPOSE.as_posix(),
        "--project-name", compose_project_name,
        "pull",
        "--ignore-pull-failures",
        "&&",
        *cmd_docker_compose_up,
    ]
    script_cmd_docker_compose_pull_up = DOCKER_COMPOSE.parent / "docker_compose_pull_up.sh"

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "--config", docker_config_json.as_posix(),
        "compose",
        "--progress",
        DOCKER_PROGRESS,
        "--file", DOCKER_COMPOSE.as_posix(),
        "--project-name", compose_project_name,
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
