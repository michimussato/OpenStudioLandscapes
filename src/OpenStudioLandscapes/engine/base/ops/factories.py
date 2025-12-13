__all__ = [
    "factory_scrape_networks",
    "factory_feature_out",
    "factory_feature_in",
    "factory_docker_config",
    "factory_compose",
    "factory_group_in",
    # "factory_compose_scope_test",
    "factory_compose_scope__features_in",
    "factory_compose_scope__CONFIG",
    "factory_compose_scope__scrape_networks",
    "factory_compose_scope__compose",
    "factory_compose_scope__docker_compose_graph",
    "factory_compose_scope__cmd",
    "factory_compose_scope__group_out",
]

import copy
import enum
import json
import pathlib
import textwrap
from collections import ChainMap
from functools import reduce
from typing import Dict, Union, Any, Generator

import yaml
from dagster import (
    AssetMaterialization,
    MetadataValue,
    OpDefinition,
    OpExecutionContext,
    Output,
    op, AssetKey,
)
from docker_compose_graph.utils import *

from OpenStudioLandscapes.engine.config.models import (
    ConfigEngine,
    DockerConfigModel,
    FeatureBaseModel, ComposeScopeBaseModel,
)
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.compose_scopes.default.constants import (
    ATTACH_SITE_TO_COMPOSE_SCOPE,
)

# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    data_type=enum.Enum,
    representer=yaml.representer.SafeRepresenter.represent_str,
)


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

        context.log.debug(f"{kwargs.keys() = }")
        context.log.debug(f"{kwargs['group_in'].keys() = }")

        # Todo
        #  - [ ] I can't serialize this nested BaseModel yet
        config_parent = kwargs["group_in"].pop("config_parent")

        # context.log.debug(f"Popping: {kwargs.pop('env') = }")
        group_in: dict = kwargs.pop("group_in")
        kwargs["group_in"] = group_in

        # I want
        # - env_base
        # - features
        # - docker_config
        # - docker_config_json
        # to stay in the root level
        # of the dict
        CONFIG: FeatureBaseModel = kwargs.pop("CONFIG")
        kwargs["config"] = CONFIG

        # Todo
        #  - [ ] replace "group_out" (i.e. with "compose_yaml" or "feature_out")
        # kwargs["compose_yaml"] = kwargs["env"]["DOCKER_COMPOSE"]

        output_name = "feature_out"

        yield Output(
            output_name=output_name,
            value=kwargs,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                **metadatavalues_from_dict(
                    context=context,
                    d=kwargs,
                ),
            },
        )

    return _op_feature_out


def factory_scrape_networks(
    name="op_scrape_networks_from_factory",
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
        description=textwrap.dedent(
            """
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
            """
        ),
        **kwargs,
    )
    def _op_scrape_networks(
        context: OpExecutionContext,
        **kwargs,
    ):

        context.log.debug(f"{kwargs = }")

        features_in = kwargs.pop("features_in")
        del kwargs
        context.log.debug(f"{features_in = }")

        # Todo:
        #  - [ ] Duplicated code `OpenStudioLandscapes.engine.base.ops.factories.factory_scrape_networks`
        #  - [ ] Duplicated code `OpenStudioLandscapes.engine.compose_scopes.default.assets.compose`

        # I want to remove
        # - env_base
        # - docker_config
        # - docker_image
        # - docker_config_json
        # from features_in
        context.log.debug(f"Popping: {features_in.pop('env_base', {}) = }")
        context.log.debug(f"Popping: {features_in.pop('config_engine', {}) = }")
        context.log.debug(f"Popping: {features_in.pop('docker_image', {}) = }")
        context.log.debug(f"Popping: {features_in.pop('docker_config_json', {}) = }")

        networks_dict: Dict = {}

        for feature, data in features_in.items():
            context.log.info(f"{features_in[feature] = }")
            CONFIG: FeatureBaseModel = data.pop("config")
            compose_file: pathlib.Path = CONFIG.docker_compose

            network_dict = get_networks_dict(
                context=context,
                compose_file=compose_file,
            )

            networks_dict.update(network_dict)

        networks_dict_yaml = yaml.safe_dump(networks_dict)

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
                # **metadatavalues_from_dict(
                #     context=context,
                #     d_serialized=json.dumps(networks_dict, default=str),
                # ),
            },
        )

    return _op_scrape_networks


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

        kwargs_json = json.dumps(kwargs, default=str)

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(kwargs_json),
                **metadatavalues_from_dict(
                    context=context,
                    d_serialized=kwargs_json,
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

        # Untangle the input kwargs:
        group_in = kwargs.pop("group_in")
        context.log.debug(group_in)
        config_engine: ConfigEngine = group_in.pop("config_engine")
        docker_config: DockerConfigModel = (
            config_engine.openstudiolandscapes__docker_config
        )

        if not isinstance(docker_config, DockerConfigModel):
            raise TypeError(
                f"Migrate to `DockerConfigModel`. "
                f"Current type: {type(docker_config)}"
            )

        context.log.debug(docker_config)

        output_name = "docker_config"

        yield Output(
            output_name=output_name,
            value=docker_config,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "docker_config": MetadataValue.json(docker_config.model_dump()),
            },
        )

    return _op_docker_config


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
        # group_in: dict = kwargs.pop("group_in")
        # env: dict = group_in.pop("env")

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
        group_out: dict = kwargs.pop(GroupIn(kw_key))
        context.log.debug(f"{group_out = }")

        group_out["feature_out_parent"] = group_out.pop("feature_out", {})

        if "config" in group_out:
            # rename "config" to "config_parent"
            group_out["config_parent"] = group_out.pop("config")
        else:
            group_out["config_parent"] = None

        context.log.debug(f"{group_out = }")

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


# def factory_compose_scope_test(
#     name="op_compose_scope_factory",
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
#     def _op_compose_scope(
#         context: OpExecutionContext,
#         **kwargs,
#     ):
#         """
#         """
#
#         # @asset
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
#         # @multi_asset
#         #################
#         # TEST_OUTPUT_1 #
#         #################
#
#         output_name = "multi_asset__test_output_1"
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
#         #################
#         # TEST_OUTPUT_2 #
#         #################
#
#         output_name = "multi_asset__test_output_2"
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
#     return _op_compose_scope


def factory_compose_scope__features_in(
    # *,
    # group_out_base,
    # asset_header: Dict,
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
        # ins=ins,
        **kwargs,
    ) -> Generator[Output | AssetMaterialization | Any, Any, None]:
        """
        """

        # # ins = context.op.inputs()
        #
        # asset_key__group_out_base = context.asset_key_for_input("group_out_base")
        # asset_header: Dict = kwargs.pop("ASSET_HEADER")
        group_out_base: Dict = kwargs.pop("group_out_base")
        env_base: Dict = group_out_base.pop("env_base")
        config_engine: ConfigEngine = group_out_base.pop("config_engine")
        docker_config_json: pathlib.Path = group_out_base.pop("docker_config_json")
        #
        # config_engine: ConfigEngine = group_out_base.pop("config_engine")
        #
        # # current_asset_key: AssetKey = context.asset_key
        # # context.asset_key_for_output(['OpenStudioLandscapes_Base', 'group_out_base'])
        # #
        # # context.asset_key_for_input("group_out_base")
        # #
        # # context.asset_key_for_output("group_out_base")
        #
        # # group_out_base = context.asset_key_for_output(output_name="group_out_base")
        #
        # # ins = kwargs.pop("ins")
        #
        # # group_out_base: dict = kwargs.pop("group_out_base")
        #
        # context.log.error(f"{context = }")
        # context.log.error(f"{dir(context) = }")
        #
        # context.pdb.set_trace()

        # context.log.info(f"{group_out_base = }")
        # context.log.info(f"{kwargs = }")

        # env_base = group_out_base.pop("env_base")
        #
        # config_engine: ConfigEngine = group_out_base.pop("config_engine")

        # docker_config_json: pathlib.Path = group_out_base.pop("docker_config_json")

        # docker_compose_yaml: Dict[str, str] = {}
        docker_compose: Dict[str, Any] = {}

        for k, v in kwargs.items():
            # remove
            # - env_base
            # - features
            # - config_engine
            # - docker_config_json
            # from kwargs dicts
            for d in [
                "env",
                "env_base",
                "features",
                "config_engine",  # pydantic.BaseModel in a nested dict is not JSON serializable yet
                "docker_config_json",
            ]:
                if d in kwargs[k]:
                    context.log.debug(f"Popping `{d}`: {kwargs[k].pop(d)}")

            docker_compose[k] = str(kwargs[k]["compose"])

        kwargs["env_base"] = env_base
        kwargs["docker_config_json"] = docker_config_json

        # @multi_asset
        ###############
        # features_in #
        ###############

        output_name = "features_in"

        # if "docker_compose_graph" in context.selected_output_names:
        #
        # yield Output(
        #     output_name=output_name,
        #     value=None,
        # )

        # yield AssetMaterialization(
        #     asset_key=context.asset_key_for_output(output_name),
        #     metadata={
        #         "__".join(
        #             context.asset_key_for_output(output_name).path
        #         ): MetadataValue.bool(False),
        #     },
        # )






        yield Output(
            output_name=output_name,
            value=kwargs,
        )

        kwargs_str = json.loads(json.dumps(kwargs, default=str))

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.json(kwargs_str),
                # "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
                "docker_compose": MetadataValue.json(docker_compose),
                # "kwargs": MetadataValue.json(kwargs_str),
            },
        )

        # #################
        # # TEST_OUTPUT_2 #
        # #################
        #
        # output_name = "test_output_2"
        #
        # # if "docker_compose_graph" in context.selected_output_names:
        #
        # yield Output(
        #     output_name=output_name,
        #     value=None,
        # )
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key_for_output(output_name),
        #     metadata={
        #         "__".join(
        #             context.asset_key_for_output(output_name).path
        #         ): MetadataValue.bool(True),
        #     },
        # )

    return _op_compose_scope__features_in


def factory_compose_scope__CONFIG(
    # *,
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
        # compose_scope: str = "default",
        **kwargs,
    ):
        """
        """
        # # context.asset_key_for_input("group_out_base")
        # #
        # # context.asset_key_for_output("features_in")
        #
        # features_in = context.asset_key_for_output(output_name="group_out_base")

        # asset_header: Dict = kwargs.pop("ASSET_HEADER")

        features_in: Dict = kwargs.pop("features_in")

        env: dict = features_in.pop("env_base", {})

        config = ComposeScopeBaseModel(
            **{
                "compose_scope": compose_scope,
                "docker_compose": pathlib.Path(
                    f"{env['DOT_LANDSCAPES']}",
                    f"{env['LANDSCAPE']}",
                    f"{asset_header['group_name']}",
                    "docker_compose",
                    "docker-compose.yml",
                ),
                "attach_pangolin_site_to_compose_scope": ATTACH_SITE_TO_COMPOSE_SCOPE,
            },
        )

        # @asset
        # yield Output(
        #     output_name="group_in",
        #     value=None,
        # )
        #
        # assert bool(kwargs) == False
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key,
        #     metadata={
        #         **metadatavalues_from_dict(
        #             context=context,
        #             d=group_out,
        #         ),
        #     },
        # )

        # @multi_asset
        ##########
        # CONFIG #
        ##########

        output_name = "CONFIG"

        # if "docker_compose_graph" in context.selected_output_names:

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

        # #################
        # # TEST_OUTPUT_2 #
        # #################
        #
        # output_name = "test_output_2"
        #
        # # if "docker_compose_graph" in context.selected_output_names:
        #
        # yield Output(
        #     output_name=output_name,
        #     value=None,
        # )
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key_for_output(output_name),
        #     metadata={
        #         "__".join(
        #             context.asset_key_for_output(output_name).path
        #         ): MetadataValue.bool(True),
        #     },
        # )

    return _op_compose_scope__CONFIG


def factory_compose_scope__scrape_networks(
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
        **kwargs,
    )
    def _op_compose_scope__scrape_networks(
        context: OpExecutionContext,
        **kwargs,
    ):
        """
        """

        # @asset
        # yield Output(
        #     output_name="group_in",
        #     value=None,
        # )
        #
        # assert bool(kwargs) == False
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key,
        #     metadata={
        #         **metadatavalues_from_dict(
        #             context=context,
        #             d=group_out,
        #         ),
        #     },
        # )

        # @multi_asset
        #################
        # TEST_OUTPUT_1 #
        #################

        output_name = "scrape_networks"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(False),
            },
        )

        # #################
        # # TEST_OUTPUT_2 #
        # #################
        #
        # output_name = "test_output_2"
        #
        # # if "docker_compose_graph" in context.selected_output_names:
        #
        # yield Output(
        #     output_name=output_name,
        #     value=None,
        # )
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key_for_output(output_name),
        #     metadata={
        #         "__".join(
        #             context.asset_key_for_output(output_name).path
        #         ): MetadataValue.bool(True),
        #     },
        # )

    return _op_compose_scope__scrape_networks


def factory_compose_scope__compose(
    name="op_compose_scope_factory__compose",
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
    def _op_compose_scope__compose(
        context: OpExecutionContext,
        **kwargs,
    ):
        """
        """

        # @asset
        # yield Output(
        #     output_name="group_in",
        #     value=None,
        # )
        #
        # assert bool(kwargs) == False
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key,
        #     metadata={
        #         **metadatavalues_from_dict(
        #             context=context,
        #             d=group_out,
        #         ),
        #     },
        # )

        # @multi_asset
        #################
        # TEST_OUTPUT_1 #
        #################

        output_name = "compose"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(False),
            },
        )

        # #################
        # # TEST_OUTPUT_2 #
        # #################
        #
        # output_name = "test_output_2"
        #
        # # if "docker_compose_graph" in context.selected_output_names:
        #
        # yield Output(
        #     output_name=output_name,
        #     value=None,
        # )
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key_for_output(output_name),
        #     metadata={
        #         "__".join(
        #             context.asset_key_for_output(output_name).path
        #         ): MetadataValue.bool(True),
        #     },
        # )

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
    ):
        """
        """

        # @asset
        # yield Output(
        #     output_name="group_in",
        #     value=None,
        # )
        #
        # assert bool(kwargs) == False
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key,
        #     metadata={
        #         **metadatavalues_from_dict(
        #             context=context,
        #             d=group_out,
        #         ),
        #     },
        # )

        # @multi_asset
        #################
        # TEST_OUTPUT_1 #
        #################

        output_name = "docker_compose_graph"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(False),
            },
        )

        #################
        # TEST_OUTPUT_2 #
        #################

        output_name = "docker_compose_graph_dot"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(True),
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
        **kwargs,
    )
    def _op_compose_scope__cmd(
        context: OpExecutionContext,
        **kwargs,
    ):
        """
        """

        # @asset
        # yield Output(
        #     output_name="group_in",
        #     value=None,
        # )
        #
        # assert bool(kwargs) == False
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key,
        #     metadata={
        #         **metadatavalues_from_dict(
        #             context=context,
        #             d=group_out,
        #         ),
        #     },
        # )

        # @multi_asset
        #################
        # TEST_OUTPUT_1 #
        #################

        output_name = "cmd_append"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(False),
            },
        )

        #################
        # TEST_OUTPUT_2 #
        #################

        output_name = "cmd_extend"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(True),
            },
        )

    return _op_compose_scope__cmd


def factory_compose_scope__group_out(
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
        **kwargs,
    )
    def _op_compose_scope__group_out(
        context: OpExecutionContext,
        **kwargs,
    ):
        """
        """

        # @asset
        # yield Output(
        #     output_name="group_in",
        #     value=None,
        # )
        #
        # assert bool(kwargs) == False
        #
        # yield AssetMaterialization(
        #     asset_key=context.asset_key,
        #     metadata={
        #         **metadatavalues_from_dict(
        #             context=context,
        #             d=group_out,
        #         ),
        #     },
        # )

        # @multi_asset
        #################
        # TEST_OUTPUT_1 #
        #################

        output_name = "group_out"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(False),
            },
        )

        #################
        # TEST_OUTPUT_2 #
        #################

        output_name = "compose_project_name"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(True),
            },
        )

        #################
        # TEST_OUTPUT_3 #
        #################

        output_name = "docker_compose_commands"

        # if "docker_compose_graph" in context.selected_output_names:

        yield Output(
            output_name=output_name,
            value=None,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key_for_output(output_name),
            metadata={
                "__".join(
                    context.asset_key_for_output(output_name).path
                ): MetadataValue.bool(True),
            },
        )

    return _op_compose_scope__group_out


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
