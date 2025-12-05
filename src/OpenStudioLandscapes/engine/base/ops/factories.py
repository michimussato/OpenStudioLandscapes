__all__ = [
    "factory_scrape_networks",
    "factory_feature_out",
    "factory_feature_in",
    "factory_docker_config",
    "factory_compose",
    "factory_group_in",
]

import copy
import enum
import json
import pathlib
import textwrap
from collections import ChainMap
from functools import reduce
from typing import Dict

from dotenv import set_key

import yaml
from dagster import (
    AssetMaterialization,
    MetadataValue,
    OpDefinition,
    OpExecutionContext,
    Output,
    op,
)
from docker_compose_graph.utils import *

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.config.validate_config import DockerConfigModel, ConfigEngine

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
        config_parent = kwargs['group_in'].pop('config_parent')

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
        config_engine = kwargs["group_in"].pop("config_engine")
        kwargs["config_engine"] = config_engine
        docker_config_json = kwargs["group_in"].pop("docker_config_json")
        kwargs["docker_config_json"] = docker_config_json
        config = kwargs.pop("CONFIG")
        kwargs["config"] = config

        # Todo
        #  - [ ] replace "group_out" (i.e. with "compose_yaml" or "feature_out")
        kwargs["compose_yaml"] = kwargs["env"]["DOCKER_COMPOSE"]

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
                    d_serialized=kwargs,
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
            compose_file = features_in[feature]["compose_yaml"]

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
        docker_config: DockerConfigModel = config_engine.openstudiolandscapes__docker_config

        if not isinstance(docker_config, DockerConfigModel):
            raise TypeError(f"Migrate to `DockerConfigModel`. "
                            f"Current type: {type(docker_config)}")

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

        env: Dict = kwargs.pop("env")
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

        # Write .env
        dot_env = DOCKER_COMPOSE.parent / ".env"
        with open(dot_env, mode="w", encoding="utf-8") as fw:
            pass

        # Add content to .env
        for k, v in env.items():
            context.log.debug(f"{k} = {v}")
            set_key(
                dotenv_path=dot_env,
                key_to_set=k,
                value_to_set=str(v),
                quote_mode=["always", "auto", "never"][1],
                export=False,
                encoding="utf-8",
            )

        with open(dot_env, "r") as fr:
            lines = fr.read()

        yield Output(
            output_name="compose",
            value=docker_dict,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
                "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
                "dot_env": MetadataValue.md(f"```\n{lines}\n```"),
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
                    d_serialized=group_out,
                ),
            },
        )

    return _op_group_in
