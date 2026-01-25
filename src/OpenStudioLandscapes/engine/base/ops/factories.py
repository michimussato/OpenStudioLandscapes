__all__ = [
    "factory_feature_out_v2",
    "factory_compose",
    "factory_cmd",
    "factory_group_in",
    "factory_feature_in",
    "factory_feature_in_parent",
    "factory_compose_scope__features_in",
    "factory_compose_scope__CONFIG",
    "factory_compose_scope__scrape_networks",
    "factory_compose_scope__compose",
    "factory_compose_scope__docker_compose_graph",
    "factory_compose_scope__cmd",
    "factory_compose_scope__group_out",
    "factory__CONFIG",
]

import base64
import copy
import enum
import itertools
import json
import os
import pathlib
import shlex
import shutil
import textwrap
from collections import ChainMap
from functools import reduce
from typing import Any, Dict, Generator, List, Type, Union

import pydot
import yaml
from dagster import (
    AssetMaterialization,
    MetadataValue,
    OpDefinition,
    OpExecutionContext,
    Output,
    op,
)
from docker_compose_graph.docker_compose_graph import DockerComposeGraph
from docker_compose_graph.utils import *

from OpenStudioLandscapes.engine.config.models import (
    ComposeScopeBaseModel,
    ConfigEngine,
    FeatureBaseModel,
)
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery import discovery
from OpenStudioLandscapes.engine.discovery.get_feature_base_model import (
    get_feature_base_model,
)
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.link.models import (
    OpenStudioLandscapesBaseOut,
    OpenStudioLandscapesFeatureIn,
    OpenStudioLandscapesFeatureOut,
)
from OpenStudioLandscapes.engine.utils import *

# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    data_type=enum.Enum,
    representer=yaml.representer.SafeRepresenter.represent_str,
)


# def factory_feature_out(
#     name="op_feature_out_from_factory",
#     ins=None,
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
#     def _op_feature_out(
#         context: OpExecutionContext,
#         **kwargs,
#     ):
#
#         context.log.debug(f"{kwargs.keys() = }")
#         context.log.debug(f"{kwargs['group_in'].keys() = }")
#
#         # Todo
#         #  - [ ] I can't serialize this nested BaseModel yet
#         config_parent = kwargs["group_in"].pop("config_parent")
#
#         # context.log.debug(f"Popping: {kwargs.pop('env') = }")
#         group_in: Dict = kwargs.pop("group_in")
#         kwargs["group_in"] = group_in
#
#         # I want
#         # - env_base
#         # - features
#         # - docker_config
#         # - docker_config_json
#         # to stay in the root level
#         # of the dict
#         CONFIG: FeatureBaseModel = kwargs.pop("CONFIG")
#         kwargs["config"] = CONFIG
#
#         # Todo
#         #  - [ ] replace "group_out" (i.e. with "compose_yaml" or "feature_out")
#         # kwargs["compose_yaml"] = kwargs["env"]["DOCKER_COMPOSE"]
#
#         context.log.debug(f"_op_feature_out {kwargs = }")
#
#         output_name = "feature_out"
#
#         yield Output(
#             output_name=output_name,
#             value=kwargs,
#         )
#
#         yield AssetMaterialization(
#             asset_key=context.asset_key_for_output(output_name),
#             metadata={
#                 **metadatavalues_from_dict(
#                     context=context,
#                     d=kwargs,
#                 ),
#             },
#         )
#
#     return _op_feature_out


def factory_feature_out_v2(
    name="op_feature_out_v2_from_factory",
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
        # code_version="2",
        **kwargs,
    )
    def _op_feature_out(
        context: OpExecutionContext,
        **kwargs,
    ):

        # group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")
        compose: Dict = kwargs.pop("compose")
        CONFIG: discovery.FeatureBaseModel = kwargs.pop("CONFIG")
        cmd_extend: List = kwargs.pop("cmd_extend")
        cmd_append: Dict = kwargs.pop("cmd_append")

        feature_out: OpenStudioLandscapesFeatureOut = OpenStudioLandscapesFeatureOut(
            compose=compose,
            config_feature=CONFIG,
            cmd_extend=cmd_extend,
            cmd_append=cmd_append,
        )

        output_name = "feature_out_v2"

        yield Output(
            output_name=output_name,
            value=feature_out,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name).path,
            metadata={
                "feature_in": MetadataValue.md(
                    f"```json\n{feature_out.model_dump_json(indent=2, fallback=str)}\n```"
                ),
            },
        )

    return _op_feature_out


def factory_cmd(
    name="op_cmd_from_factory",
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
    def _op__cmd(
        context: OpExecutionContext,
        **kwargs,
    ):

        ##############
        # cmd_append #
        ##############

        ret_cmd_append = {"cmd": [], "exclude_from_quote": ["$(which docker)"]}

        output_name = "cmd_append"

        yield Output(
            output_name=output_name,
            value=ret_cmd_append,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.json(ret_cmd_append),
            },
        )

        ##############
        # cmd_extend #
        ##############

        output_name = "cmd_extend"

        ret_cmd_extend = []

        yield Output(
            output_name=output_name,
            value=ret_cmd_extend,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.json(ret_cmd_extend),
            },
        )

    return _op__cmd


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

        compose_networks = kwargs.pop("compose_networks")
        compose_maps = kwargs.pop("compose_maps")
        CONFIG: FeatureBaseModel = kwargs.pop("CONFIG")

        DOCKER_COMPOSE: pathlib.Path = CONFIG.docker_compose_expanded
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

        docker_dict_dump = json.dumps(docker_dict, indent=2, default=str)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "docker_json": MetadataValue.md(f"```json\n{docker_dict_dump}\n```"),
                "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
                "docker_compose_yaml": MetadataValue.path(DOCKER_COMPOSE),
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

        context.log.debug(f"{ins = }")
        context.log.debug(f"{kwargs = }")

        kw_keys = list(kwargs.keys())

        context.log.debug(f"{kw_keys = }")

        # We expect an enums.GroupIn value here
        # Make sure there is only one key
        if len(kw_keys) == 1:
            kw_key = kw_keys[0]
        else:
            raise NotImplementedError("We expect `kw_keys` to be exactly 1.")

        # parent env would be:
        # kwargs[kw_key]["env"]

        # Access Enum value by key:
        # https://stackoverflow.com/a/38716384
        group_out: Dict = kwargs.pop(GroupIn(kw_key))

        group_out["feature_out_parent"] = group_out.pop("feature_out", {})

        if "config" in group_out:
            # rename "config" to "config_parent"
            group_out["config_parent"] = group_out.pop("config")
        else:
            group_out["config_parent"] = None

        context.log.debug(f"_op_group_in {group_out = }")

        yield Output(
            output_name="group_in",
            value=group_out,
        )

        assert bool(kwargs) == False

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                **metadatavalues_from_dict(
                    context=context,
                    d=group_out,
                ),
            },
        )

    return _op_group_in


def factory_feature_in(
    name="op_feature_in_factory",
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
        """
        This is the entry point for a Feature.
        Just forwards the data we get from the upstream `group_out` asset.
        """

        group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")

        feature_in_parent: Union[None, OpenStudioLandscapesFeatureOut] = kwargs.pop(
            "feature_in_parent", None
        )

        feature_in: OpenStudioLandscapesFeatureIn = OpenStudioLandscapesFeatureIn(
            openstudiolandscapes_base=group_out_base,
            feature_in_parent=feature_in_parent,
        )

        output_name = "feature_in"

        yield Output(
            output_name=output_name,
            value=feature_in,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name).path,
            metadata={
                "feature_in": MetadataValue.md(
                    f"```json\n{feature_in.model_dump_json(indent=2, fallback=str)}\n```"
                ),
            },
        )

    return _op_feature_in


def factory_feature_in_parent(
    CONFIG_PARENT: Type[FeatureBaseModel],
    name="op_feature_in_parent_factory",
    ins=None,
    **kwargs,
) -> OpDefinition:
    """
    https://docs.dagster.io/guides/build/ops#op-factory

    Args:
        CONFIG_PARENT: FeatureBaseModel subclass
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
    def _op_feature_in_parent(
        context: OpExecutionContext,
        **kwargs,
    ):
        """ """

        feature_in_parent: Union[None, OpenStudioLandscapesFeatureOut] = kwargs[
            "feature_in"
        ].feature_in_parent

        config_parent: Union[None, CONFIG_PARENT] = feature_in_parent.config_feature

        #####################
        # feature_in_parent #
        #####################

        output_name = "feature_in_parent"

        yield Output(
            output_name=output_name,
            value=feature_in_parent,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.md(
                    f"```json\n{feature_in_parent.model_dump_json(indent=2, fallback=str)}\n```"
                ),
            },
        )

        #################
        # CONFIG_PARENT #
        #################

        output_name = "CONFIG_PARENT"

        yield Output(
            output_name=output_name,
            value=config_parent,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.md(
                    f"```json\n{config_parent.model_dump_json(indent=2, fallback=str)}\n```"
                ),
            },
        )

    return _op_feature_in_parent


def factory_compose_scope__features_in(
    name="op_compose_scope_factory__features_in",
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
    def _op_compose_scope__features_in(
        context: OpExecutionContext,
        **kwargs,
    ) -> Generator[Output | AssetMaterialization | Any, Any, None]:
        """ """

        # # ins = context.op.inputs()
        #
        # asset_key__group_out_base = context.asset_key_for_input("group_out_base")
        # asset_header: Dict = kwargs.pop("ASSET_HEADER")
        # group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")
        # env_base: Dict = group_out_base.env
        # config_engine: ConfigEngine = group_out_base.config_engine
        # docker_config_json: pathlib.Path = group_out_base.docker_config_json

        docker_compose: Dict[str, Any] = {}

        metadata = {}

        k: str
        v: OpenStudioLandscapesFeatureOut
        for k, v in kwargs.items():
            context.log.debug(f"{k = }")
            context.log.debug(f"{v = }")

            docker_compose[k] = v.compose
            metadata[f"compose_{k}"] = MetadataValue.json(v.compose)

        # kwargs["env_base"] = env_base
        # kwargs["docker_config_json"] = docker_config_json

        ###############
        # features_in #
        ###############

        output_name = "features_in"

        yield Output(
            output_name=output_name,
            value=kwargs,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                **metadata,
            },
        )

        # ##################
        # # group_out_base #
        # ##################
        #
        # output_name = "group_out_base"
        #
        # yield Output(
        #     output_name=output_name,
        #     value=group_out_base,
        # )
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key_for_output(output_name),
        #     # metadata={
        #     #     **metadata,
        #     # },
        # )

    return _op_compose_scope__features_in


def factory_compose_scope__CONFIG(
    compose_scope: str,
    asset_header: Dict,
    name="op_compose_scope_factory__CONFIG",
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
    def _op_compose_scope__CONFIG(
        context: OpExecutionContext,
        **kwargs,
    ) -> Generator[Output | AssetMaterialization | Any, Any, None]:
        """ """

        context.log.debug(f"{kwargs = }")

        features_in: Dict = kwargs.pop("features_in")
        context.log.debug(f"{features_in = }")

        group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")
        context.log.debug(f"{group_out_base = }")

        config_engine: ConfigEngine = group_out_base.config_engine

        env: Dict = group_out_base.env

        config = ComposeScopeBaseModel(
            **{
                "env": env,
                "compose_scope": compose_scope,
                "docker_compose": pathlib.Path(
                    f"{env['DOT_LANDSCAPES']}",
                    f"{env['LANDSCAPE']}",
                    f"{asset_header['group_name']}",
                    "docker_compose",
                    "docker-compose.yml",
                ),
                "config_engine": config_engine,
            },
        )

        ##########
        # CONFIG #
        ##########

        output_name = "CONFIG"

        yield Output(
            output_name=output_name,
            value=config,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.md(
                    f"```json\n{json.dumps(config.model_dump(mode='json'), indent=2, default=str)}\n```"
                ),
            },
        )

    return _op_compose_scope__CONFIG


def factory_compose_scope__scrape_networks(
    # compose_scope: str,
    name="op_compose_scope_factory__scrape_networks",
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
        description=textwrap.dedent("""
            Recursively scrape a hierarchical (`include`) Docker Compose 
            YAML tree for `networks` at the root level, as in:
            
            ```yaml
            networks:
              kitsu:
                name: network_kitsu
            ```
            
            This is needed for the Pangolin `newt` service so that
            it can discover services.
            
            See:
            - [https://github.com/fosrl/newt]()
            - [https://docs.pangolin.net/manage/sites/install-site#docker-installation]()
            """),
        **kwargs,
    )
    def _op_compose_scope__scrape_networks(
        context: OpExecutionContext,
        **kwargs,
    ) -> Generator[Output | AssetMaterialization | Any, Any, None]:
        """ """

        # group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")

        context.log.debug(f"{kwargs = }")

        features_in: Dict[str, OpenStudioLandscapesFeatureOut] = kwargs.pop(
            "features_in"
        )
        del kwargs
        context.log.debug(f"{features_in = }")
        # env: Dict = group_out_base.env

        # Todo:
        #  - [ ] Duplicated code `OpenStudioLandscapes.engine.base.ops.factories.factory_scrape_networks`
        #  - [ ] Duplicated code `OpenStudioLandscapes.engine.compose_scopes.default.assets.compose`

        # I want to remove
        # - env_base
        # - docker_config
        # - docker_image
        # - docker_config_json
        # from features_in
        # context.log.debug(f"Popping: {features_in.pop('env_base') = }")
        # context.log.debug(f"Popping: {features_in.pop('config_engine') = }")
        # context.log.debug(f"Popping: {features_in.pop('docker_image') = }")
        # context.log.debug(f"Popping: {features_in.pop('docker_config_json') = }")

        networks_dict: Dict = {}

        # feature: str
        # data: OpenStudioLandscapesFeatureOut
        for feature, data in features_in.items():
            context.log.info(f"{features_in[feature] = }")
            CONFIG: FeatureBaseModel = data.config_feature
            compose_file: pathlib.Path = CONFIG.docker_compose_expanded

            network_dict = get_networks_dict(
                context=context,
                compose_file=compose_file,
            )

            networks_dict.update(network_dict)

        networks_dict_yaml = yaml.safe_dump(networks_dict)

        ###################
        # scrape_networks #
        ###################

        output_name = "scrape_networks"

        yield Output(
            output_name=output_name,
            value=networks_dict,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(networks_dict),
                "networks_dict_yaml": MetadataValue.md(
                    f"```yaml\n{networks_dict_yaml}\n```"
                ),
            },
        )

    return _op_compose_scope__scrape_networks


def factory_compose_scope__compose(
    compose_scope: str,
    name="op_compose_scope_factory__compose",
    ins=None,
    **kwargs,
) -> OpDefinition:
    """
    https://docs.dagster.io/guides/build/ops#op-factory

    Args:
        compose_scope: str
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
    def _op_compose_scope__compose(
        context: OpExecutionContext,
        **kwargs,
    ) -> Generator[Output | AssetMaterialization | Any, Any, None]:
        """ """

        group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")

        context.log.debug(f"{kwargs = }")
        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")
        features_in: Dict[str, OpenStudioLandscapesFeatureOut] = kwargs.pop(
            "features_in"
        )
        # scrape_networks: Dict = kwargs.pop("scrape_networks")

        env: Dict = group_out_base.env

        # Todo:
        #  - [ ] Duplicated code `OpenStudioLandscapes.engine.base.ops.factories.factory_scrape_networks`
        #  - [ ] Duplicated code `OpenStudioLandscapes.engine.compose_scopes.default.assets.compose`

        DOCKER_COMPOSE: pathlib.Path = CONFIG.docker_compose

        DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

        compose_files = []
        _compose_networks = set()

        for feature, data in features_in.items():
            CONFIG_FEATURE: FeatureBaseModel = data.config_feature
            context.log.info(f"{CONFIG_FEATURE.feature_name = }")
            compose_file = CONFIG_FEATURE.docker_compose_expanded
            compose_files.append(compose_file)

        includes = []
        dot_landscapes = pathlib.Path(env["DOT_LANDSCAPES"])

        # Convert absolute paths in `include` to
        # relative ones
        for path in compose_files:
            rel_path = get_relative_path_via_common_root(
                context=context,
                path_src=DOCKER_COMPOSE,
                path_dst=pathlib.Path(path),
                path_common_root=dot_landscapes,
            )

            include_ = {
                "project_directory": rel_path.parent.as_posix(),
                "path": [
                    rel_path.as_posix(),
                ],
            }

            includes.append(include_)

        docker_dict_include: Dict = {
            "include": includes,
        }

        # Todo
        #  - [ ] this is not very elegant yet...

        # if "wrapper_alloy" in kwargs:
        wrapper_alloy = kwargs.pop("wrapper_alloy", {})

        # if "wrapper_newt" in kwargs:
        wrapper_newt = kwargs.pop("wrapper_newt", {})

        docker_chainmap = ChainMap(
            wrapper_alloy,
            wrapper_newt,
            docker_dict_include,
        )

        docker_chainmap_dict = reduce(deep_merge, docker_chainmap.maps)
        #
        # docker_yaml = yaml.dump(docker_chainmap_dict)

        docker_yaml_include = yaml.safe_dump(docker_chainmap_dict)

        # Write docker-compose.yaml
        with open(DOCKER_COMPOSE, mode="w", encoding="utf-8") as fw:
            fw.write(docker_yaml_include)

        ###########
        # COMPOSE #
        ###########

        output_name = "compose"

        yield Output(
            output_name=output_name,
            value=docker_chainmap_dict,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.json(docker_chainmap_dict),
                "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml_include}\n```"),
                "includes": MetadataValue.json(includes),
            },
        )

    return _op_compose_scope__compose


def factory_compose_scope__docker_compose_graph(
    name="op_compose_scope_factory__docker_compose_graph",
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
    def _op_compose_scope__docker_compose_graph(
        context: OpExecutionContext,
        **kwargs,
    ) -> Generator[
        Output[pydot.Dot] | Output[pathlib.Path] | AssetMaterialization, None, None
    ]:
        """ """

        group_out: pathlib.Path = kwargs.pop("group_out")
        compose_project_name: str = kwargs.pop("compose_project_name")

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
            context.log.exception(e)
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
            context.log.exception(e)
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
            context.log.exception(e)
            raise FileNotFoundError("Is Graphviz installed?") from e

        ########################
        # docker_compose_graph #
        ########################

        output_name = "docker_compose_graph"

        yield Output(
            output_name=output_name,
            value=dcg.graph,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "svg": MetadataValue.md(svg_md),
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.json(str(dcg.graph)),
                "svg_path": MetadataValue.path(svg),
                "png_path": MetadataValue.path(png),
            },
        )

        ############################
        # docker_compose_graph_dot #
        ############################

        output_name = "docker_compose_graph_dot"

        yield Output(
            output_name=output_name,
            value=dot,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.path(dot),
            },
        )

    return _op_compose_scope__docker_compose_graph


def factory_compose_scope__cmd(
    name="op_compose_scope_factory__cmd",
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
        description="Creates flattend versions of all `cmd_append` and `cmd_extend` assets",
        **kwargs,
    )
    def _op_compose_scope__cmd(
        context: OpExecutionContext,
        **kwargs,
    ) -> Generator[Output | AssetMaterialization | Any, Any, None]:
        """ """

        features_in = kwargs.pop("features_in")

        cmd_extend_: List[List] = []
        cmd_append_cmd: List[Dict] = []
        cmd_append_exclude: List[Dict] = []

        feature: str
        feature_out: OpenStudioLandscapesFeatureOut

        for feature, feature_out in features_in.items():
            context.log.debug(f"{feature = }")
            context.log.debug(f"{feature_out = }")
            cmd_extend_.append(feature_out.cmd_extend)
            cmd_append_cmd.extend(feature_out.cmd_append["cmd"])
            cmd_append_exclude.extend(feature_out.cmd_append["exclude_from_quote"])

        # Flatten nested list and remove duplicate entries
        cmd_extend: List = list(set(list(itertools.chain(*cmd_extend_))))
        # Flatten nested dict
        cmd_append: Dict = dict()
        cmd_append["cmd"] = cmd_append_cmd
        cmd_append["exclude_from_quote"] = cmd_append_exclude

        ##############
        # cmd_append #
        ##############

        output_name = "cmd_append"

        yield Output(
            output_name=output_name,
            value=cmd_append,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.json(cmd_append),
            },
        )

        ##############
        # cmd_extend #
        ##############

        output_name = "cmd_extend"

        yield Output(
            output_name=output_name,
            value=cmd_extend,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.json(cmd_extend),
            },
        )

    return _op_compose_scope__cmd


def factory_compose_scope__group_out(
    compose_scope: str,
    name="op_compose_scope_factory__group_out",
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
        description=textwrap.dedent(f"""
            Environment variable  
            > `OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE={bool(int(os.environ.get('OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE', 0)))}`
            
            If `OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE` is `True`,
            __set the following environment variables manually__ when launching the Landscape:
            
            > ```shell
            > OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__NEWT_ID
            > OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__NEWT_SECRET
            > OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__PANGOLIN_ENDPOINT
            > ```
            
            A successful registration is confirmed with the following log entry:
            
            > ```shell
            > [...]
            > INFO: 2025/12/14 10:59:49 Tunnel connection to server established successfully!
            > [...]
            > ```
            
            More about Pangolin Sites here
            - [https://docs.pangolin.net/manage/sites]()
            
            ---
            
            Without setting these variables, the ComposeScope may work
            and will result in the inability for the ComposeScope to 
            register to the Pangolin Site.
            
            These are log messages you're potentially going to see:
            
            > ```shell
            > [...]
            > WARN[0000] The "OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__NEWT_ID" variable is not set. Defaulting to a blank string. 
            > WARN[0000] The "OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__NEWT_SECRET" variable is not set. Defaulting to a blank string. 
            > WARN[0000] The "OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__PANGOLIN_ENDPOINT" variable is not set. Defaulting to a blank string.
            > [...]
            > ```
            
            and
            
            > ```shell
            > [...]
            > ERROR: 2025/12/14 10:48:29 Failed to connect: failed to get token: failed to request new token: Post "/api/v1/auth/newt/get-token": unsupported protocol scheme "". Retrying in 3s...
            > [...]
            > ```
            """),
        **kwargs,
    )
    def _op_compose_scope__group_out(
        context: OpExecutionContext,
        **kwargs,
    ) -> Generator[Output | AssetMaterialization | Any, Any, None]:
        """ """

        group_out_base: OpenStudioLandscapesBaseOut = kwargs.pop("group_out_base")
        compose = kwargs.pop("compose")
        cmd_append: Dict = kwargs.pop("cmd_append")
        cmd_extend: List = kwargs.pop("cmd_extend")
        CONFIG: ComposeScopeBaseModel = kwargs.pop("CONFIG")
        features_in = kwargs.pop("features_in")

        del compose

        env = CONFIG.env
        docker_config_json: pathlib.Path = group_out_base.docker_config_json

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
            f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{compose_scope}"
        )

        group_names_by_key_dict = context.assets_def.group_names_by_key
        # Results in:
        # Single Output:
        # {AssetKey(['OpenCue', 'group_out']): 'OpenCue'}
        # Multiple Outputs:
        # {AssetKey(['Compose_default', 'group_out']): 'Compose_default', AssetKey(['Compose_default', 'compose_project_name']): 'Compose_default'}
        context.log.debug(group_names_by_key_dict)

        cmd_docker_compose_logs = [
            "$(which docker)",
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
        script_cmd_docker_compose_logs = (
            DOCKER_COMPOSE.parent / "docker_compose_logs.sh"
        )

        cmd_docker_compose_up = [
            "$(which docker)",
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
            }["cmd_extend"],
            *cmd_append["cmd"],
            "&&",
            *cmd_docker_compose_logs,
        ]
        # Results in something like:
        # $(which docker) \
        #     --config ../../../2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite/OpenStudioLandscapes/OpenStudioLandscapes_Base__docker_config_json compose \
        #     --progress plain \
        #     --file ../../../2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite/ComposeScope_worker/docker_compose/docker-compose.yml \
        #     --project-name 2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite-worker \
        #     up \
        #     --remove-orphans \
        #     --detach \
        #     && /usr/bin/sudo /usr/bin/nsenter \
        #     --target $($(which docker) inspect -f '{{ .State.Pid }}' flamenco-worker-001.2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite) \
        #     --uts hostname $(hostname)-flamenco-worker-001 \
        #     && /usr/bin/sudo /usr/bin/nsenter \
        #     --target $($(which docker) inspect -f '{{ .State.Pid }}' opencue-rqd-worker-001.2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite) \
        #     --uts hostname $(hostname)-opencue-rqd-worker-001 \
        #     && $(which docker) \
        #     --config ../../../2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite/OpenStudioLandscapes/OpenStudioLandscapes_Base__docker_config_json \
        #     compose \
        #     --progress plain \
        #     --file ../../../2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite/ComposeScope_worker/docker_compose/docker-compose.yml \
        #     --project-name 2026-01-20_00-42-28__clumsy-peaceful-volcano-sprite-worker \
        #     logs \
        #     --follow
        script_cmd_docker_compose_up = DOCKER_COMPOSE.parent / "docker_compose_up.sh"

        cmd_docker_compose_restart = [
            "$(which docker)",
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
            "$(which docker)",
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
            "$(which docker)",
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
        script_cmd_docker_compose_down = (
            DOCKER_COMPOSE.parent / "docker_compose_down.sh"
        )

        systemd_unit = textwrap.dedent(f"""
            [Unit]
            # More info on systemd specifiers:
            # - https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html?__goaway_challenge=meta-refresh&__goaway_id=af831620b51d37fbc05006860cc19eca&__goaway_referer=https%3A%2F%2Fduckduckgo.com%2F#Specifiers
            Description=OpenStudioLandscapes Worker Systemd Unit (%n) - {env['LANDSCAPE']}
            After=docker.service
            Wants=docker.service
            ReloadPropagatedFrom=docker.service
            
            [Service]
            Type=simple
            Restart=always
            ##################################################################
            # CHANGE ME:                                                     #
            # set SUDO_PASS= to the correct value                            #
            # Security concerns:                                             #
            # - this is a WIP approach and not final                         #
            # - will probably be changed to                                  #
            #   EnvironmentFile with root only read access                   #
            #   like ~/.config/OpenStudioLandscapes/ComposeScope_default.env #
            Environment="SUDO_PASS="
            # Environment="LANDSCAPE_ID=\${env['LANDSCAPE']}"
            Environment="OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__PANGOLIN_ENDPOINT="
            Environment="OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__NEWT_ID="
            Environment="OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{compose_scope.upper()}__NEWT_SECRET="
            ################################################################
            RestartSec=5
            # WorkingDirectory=/data/share/nfs/.openstudiolandscapes/.landscapes
            # for this service, the scripts need
            ExecStart=/usr/bin/bash -lc "echo \${{SUDO_PASS}} | {script_cmd_docker_compose_up.as_posix()}"
            ExecStop=/usr/bin/bash -lc "echo \${{SUDO_PASS}} | {script_cmd_docker_compose_down.as_posix()}"
            
            [Install]
            WantedBy=default.target
            """)

        systemd_unit_shell = textwrap.dedent(f"""
            # Disable currently running Unit with:
            systemctl --user disable --now openstudiolandscapes-{compose_scope}@${{USER}}.service
            # Install systemd unit with:
            sudo tee /etc/systemd/user/openstudiolandscapes-{compose_scope}@.service << EOF
            {textwrap.indent(systemd_unit, prefix='            ')}
            EOF
            systemctl --user daemon-reload
            systemd-analyze --user verify openstudiolandscapes-{compose_scope}@${{USER}}.service
            # Enable Unit with:
            # systemctl --user enable --now openstudiolandscapes-{compose_scope}@${{USER}}.service
            # Check Journal with:
            # journalctl --user -fu openstudiolandscapes-{compose_scope}@${{USER}}.service
            """)

        # Todo
        #  cmd_docker_exec_it = [
        #      "$(which docker)",
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
        docker_script["script"] += (
            "# Export environment variables required by *some* docker-compose files\n"
            "# as well as /usr/bin/nsenter --uts hostname\n"
        )
        docker_script["script"] += "HOSTNAME=$($(which hostname) --fqdn)\n"
        docker_script["script"] += "export HOSTNAME\n"
        # docker_script["script"] += "\n"

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
            script_dict: Dict[str, Union[str, List, pathlib.Path]],
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
                fw.write('echo "Working Directory: $(pwd)"\n')
                fw.write("\n")

                cmd_str = " ".join(
                    shlex.quote(s) if not s in cmd_append["exclude_from_quote"] else s
                    for s in script_dict["cmd"]
                )

                context.log.debug(f"{cmd_str = }")

                cmd_str_replaced = cmd_str.replace(
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
                    docker_config_json.as_posix(),
                    get_relative_path_via_common_root(
                        context=context,
                        path_src=script_cmd_docker_compose_up,
                        path_dst=docker_config_json,
                        path_common_root=pathlib.Path(env["DOT_LANDSCAPES"]),
                    ).as_posix(),
                )

                context.log.debug(f"{cmd_str_replaced = }")

                fw.write(f"{cmd_str_replaced}\n")
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
                    context.asset_key_for_output(
                        script_dict["asset_key_for_output"]
                    ).path
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

        #############
        # group_out #
        #############

        output_name = "group_out"

        yield Output(
            output_name=output_name,
            value=DOCKER_COMPOSE,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.path(DOCKER_COMPOSE),
                "root_dir": MetadataValue.path(DOCKER_COMPOSE.parent),
                # "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
                "scripts": MetadataValue.json(scripts),
            },
        )

        ########################
        # compose_project_name #
        ########################

        output_name = "compose_project_name"

        yield Output(
            output_name=output_name,
            value=compose_project_name,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.path(compose_project_name),
            },
        )

        ###########################
        # docker_compose_commands #
        ###########################

        output_name = "docker_compose_commands"

        yield Output(
            output_name=output_name,
            value={
                "cmd_docker_compose_up": cmd_docker_compose_up,
                "cmd_docker_compose_restart": cmd_docker_compose_restart,
                "cmd_docker_compose_pull_up": cmd_docker_compose_pull_up,
                "cmd_docker_compose_down": cmd_docker_compose_down,
                "cmd_docker_compose_logs": cmd_docker_compose_logs,
            },
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "script_cmd_docker_compose_up": MetadataValue.path(
                    script_cmd_docker_compose_up
                ),
                "script_cmd_docker_compose_down": MetadataValue.path(
                    script_cmd_docker_compose_down
                ),
                "script_cmd_docker_compose_up_down": MetadataValue.path(
                    "; ".join(
                        [
                            script_cmd_docker_compose_up.as_posix(),
                            script_cmd_docker_compose_down.as_posix(),
                        ]
                    )
                ),
                "script_cmd_docker_compose_restart": MetadataValue.path(
                    script_cmd_docker_compose_restart
                ),
                "script_cmd_docker_compose_pull_up": MetadataValue.path(
                    script_cmd_docker_compose_pull_up
                ),
                "script_cmd_docker_compose_logs": MetadataValue.path(
                    script_cmd_docker_compose_logs
                ),
            },
        )

        ################
        # systemd_unit #
        ################

        output_name = "systemd_unit"

        yield Output(
            output_name=output_name,
            value=systemd_unit,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "systemd_unit": MetadataValue.md(f"```ini\n{systemd_unit_shell}```"),
            },
        )

    return _op_compose_scope__group_out


def factory__CONFIG(
    CONFIG_STR: str,
    search_model_of_type: Type[discovery.FeatureBaseModel],
    name="op_factory__CONFIG",
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
        description=textwrap.dedent(f"""
Reads options from a `config.yml` on your hard drive.
If the custom `config.yml` does not exist, it 
will be created locally containing default options.

---

For reference, the default `Config` values are as follows:

> __These default `Config` values **do not reflect your
> actual configuration** specified in the `config.yml` file.__
        
```yaml
{CONFIG_STR}
```
"""),
        **kwargs,
    )
    def _op__CONFIG(
        context: OpExecutionContext,
        **kwargs,
    ):
        """ """

        # if config_parent is None:
        #     pass
        # else:
        #     pass

        feature_in: OpenStudioLandscapesFeatureIn = kwargs.get("feature_in")

        env: Dict = feature_in.openstudiolandscapes_base.env

        config_validated: discovery.FeatureBaseModel = get_feature_base_model(
            context=context,
            discovered_models=discovery.DISCOVERED_MODELS,
            search_instance_type=search_model_of_type,
        )

        config_validated.env = env

        ##########
        # CONFIG #
        ##########

        output_name = "CONFIG"

        yield Output(
            output_name=output_name,
            value=config_validated,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.md(
                    f"```yaml\n{yaml.safe_dump(json.loads(config_validated.model_dump_json(fallback=str, indent=2)))}\n```"
                ),
            },
        )

        # feature_in_parent: Union[None, OpenStudioLandscapesFeatureOut] = feature_in.feature_in_parent
        #
        # if feature_in_parent is not None:
        #
        #     config_validated_parent: discovery.FeatureBaseModel = feature_in_parent.config_feature
        #
        #     #################
        #     # CONFIG_PARENT #
        #     #################
        #
        #     output_name = "CONFIG_PARENT"
        #
        #     yield Output(
        #         output_name=output_name,
        #         value=config_validated_parent,
        #     )
        #
        #     yield AssetMaterialization(
        #         asset_key=context.asset_key_for_output(output_name),
        #         metadata={
        #             "__".join(
        #                 context.asset_key_for_output(output_name).path
        #                 ): MetadataValue.md(
        #                 f"```yaml\n{yaml.safe_dump(json.loads(config_validated_parent.model_dump_json(fallback=str, indent=2)))}\n```"
        #             ),
        #         },
        #     )

    return _op__CONFIG


# # TEMPLATE (FACTORY)
# def factory_compose_scope__template(
#     name="op_compose_scope_factory__template",
#     ins=None,
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
#     def _op_compose_scope__template(
#         context: OpExecutionContext,
#         **kwargs,
#     ):
#         """
#         """
#
#         # @asset (single) pattern
#         # yield Output(
#         #     output_name="group_in",
#         #     value=None,
#         # )
#         #
#         # assert bool(kwargs) == False
#         #
#         # yield AssetMaterialization(
#         #     asset_key=context.asset_key,
#         #     metadata={
#         #         **metadatavalues_from_dict(
#         #             context=context,
#         #             d=group_out,
#         #         ),
#         #     },
#         # )
#
#         # @multi_asset pattern
#         ##################
#         # template_out_1 #
#         ##################
#
#         output_name = "template_out_1"
#
#         # if "docker_compose_graph" in context.selected_output_names:
#
#         yield Output(
#             output_name=output_name,
#             value=None,
#         )
#
#         yield AssetMaterialization(
#             asset_key=context.asset_key_for_output(output_name),
#             metadata={
#                 "__".join(
#                     context.asset_key_for_output(output_name).path
#                 ): MetadataValue.bool(False),
#             },
#         )
#
#         ##################
#         # template_out_n #
#         ##################
#
#         output_name = "template_out_n"
#
#         # if "docker_compose_graph" in context.selected_output_names:
#
#         yield Output(
#             output_name=output_name,
#             value=None,
#         )
#
#         yield AssetMaterialization(
#             asset_key=context.asset_key_for_output(output_name),
#             metadata={
#                 "__".join(
#                     context.asset_key_for_output(output_name).path
#                 ): MetadataValue.bool(True),
#             },
#         )
#
#     return _op_compose_scope__template
