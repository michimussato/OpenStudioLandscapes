import enum
import json
import pathlib
import textwrap
from typing import Any, Dict, Generator, List, MutableMapping

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
    get_dagster_logger,
)

LOGGER = get_dagster_logger(__name__)

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine.base.ops import (
    op_docker_compose_graph,
)
from OpenStudioLandscapes.engine.common_assets.group_out_compose_scope import (
    get_group_out,
)
from OpenStudioLandscapes.engine.common_assets.scrape_networks import (
    get_scrape_networks,
)
from OpenStudioLandscapes.engine.compose_scopes.default.constants import (
    ATTACH_SITE_TO_COMPOSE_SCOPE,
)
from OpenStudioLandscapes.engine.config.models import (
    ComposeScopeBaseModel,
    FeatureBaseModel,
)
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.pangolin import *

# Todo:
#  - [ ] get assets from common_assets


# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    enum.Enum,
    yaml.representer.SafeRepresenter.represent_str,
)

feature_ins = get_dynamic_ins(
    imported_features=discovery.DISCOVERED_MODELS,
)

LOGGER.error(f"{feature_ins = }")
# feature_ins = {'default': {'OpenStudioLandscapes_Kitsu': AssetIn(key=AssetKey(['Kitsu', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_Watchtower': AssetIn(key=AssetKey(['Watchtower', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_VERT': AssetIn(key=AssetKey(['VERT', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}}

if bool(feature_ins):

    for compose_scope, features in feature_ins.items():
        # Todo
        #  - [ ] This most likely needs a factory

        if compose_scope != ["default", "test"][0]:
            continue

        LOGGER.error(f"{compose_scope = }")
        LOGGER.error(f"{features = }")

        GROUP_COMPOSE = f"ComposeScope_{compose_scope}"
        KEY_COMPOSE = [GROUP_COMPOSE]

        ASSET_HEADER_COMPOSE = {
            "group_name": GROUP_COMPOSE,
            "key_prefix": KEY_COMPOSE,
            "compute_kind": "python",
        }

        @asset(
            **ASSET_HEADER_COMPOSE,
            ins={
                "features_in": AssetIn(
                    AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "features_in"]),
                ),
            },
            description=textwrap.dedent(
                """
                Reads options from a custom `config.yml`.
                If the custom `config.yml` does not exist, it
                will be created locally containing default options.
                """
            ),
        )
        def CONFIG(
            context: AssetExecutionContext,
            features_in: dict,  # pylint: disable=redefined-outer-name
        ) -> Generator[
            Output[ComposeScopeBaseModel] | AssetMaterialization,
            None,
            None,
        ]:

            env: dict = features_in.pop("env_base", {})

            config = ComposeScopeBaseModel(
                **{
                    "compose_scope": compose_scope,
                    "docker_compose": pathlib.Path(
                        f"{env['DOT_LANDSCAPES']}",
                        f"{env['LANDSCAPE']}",
                        f"{ASSET_HEADER_COMPOSE['group_name']}",
                        "docker_compose",
                        "docker-compose.yml",
                    ),
                    "attach_pangolin_site_to_compose_scope": ATTACH_SITE_TO_COMPOSE_SCOPE,
                },
            )

            yield Output(config)

            yield AssetMaterialization(
                asset_key=context.asset_key,
                metadata={
                    "__".join(context.asset_key.path): MetadataValue.md(
                        f"```json\n{json.dumps(config.model_dump(mode='json'), indent=2, default=str)}\n```"
                    ),
                },
            )

        # Todo
        #  - [ ] Move to factory
        @asset(
            **ASSET_HEADER_COMPOSE,
            ins={
                "features_in": AssetIn(
                    AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "features_in"]),
                ),
                "scrape_networks": AssetIn(
                    AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "scrape_networks"]),
                ),
                "CONFIG": AssetIn(
                    AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "CONFIG"]),
                ),
            },
            description=textwrap.dedent(
                f"""
                If `OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE` is `True`,
                set the following environment variables before launching the Landscape:
                
                ```shell
                OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{str('COMPOSE_SCOPE').upper()}__NEWT_ID=$NEWT_ID \\
                OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{str('COMPOSE_SCOPE').upper()}__NEWT_SECRET=$NEWT_SECRET \\
                OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{str('COMPOSE_SCOPE').upper()}__PANGOLIN_ENDPOINT=$PANGOLIN_ENDPOINT \\
                <docker_compose_commands>
                ```
                
                See [Install Site](https://docs.pangolin.net/manage/sites/install-site#docker-compose)
                for more info.
                """
            ),
        )
        def compose(
            context: AssetExecutionContext,
            features_in: dict,  # pylint: disable=redefined-outer-name
            scrape_networks: dict,  # pylint: disable=redefined-outer-name
            CONFIG: ComposeScopeBaseModel,  # pylint: disable=redefined-outer-name
        ) -> Generator[
            Output[MutableMapping[str, List[MutableMapping[str, List]]]]
            | AssetMaterialization,
            None,
            None,
        ]:
            """ """

            env: dict = features_in.pop("env_base", {})

            # Todo:
            #  - [ ] Duplicated code `OpenStudioLandscapes.engine.base.ops.factories.factory_scrape_networks`
            #  - [ ] Duplicated code `OpenStudioLandscapes.engine.compose_scopes.default.assets.compose`

            # context.log.debug(f"Popping: {features_in.pop('env_base', {}) = }")
            context.log.debug(f"Popping: {features_in.pop('config_engine', {}) = }")
            context.log.debug(f"Popping: {features_in.pop('docker_image', {}) = }")
            context.log.debug(
                f"Popping: {features_in.pop('docker_config_json', {}) = }"
            )

            DOCKER_COMPOSE: pathlib.Path = CONFIG.docker_compose

            DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

            compose_files = []
            _compose_networks = set()

            for feature, data in features_in.items():
                CONFIG_: FeatureBaseModel = data["config"]
                context.log.info(f"{CONFIG_.feature_name = }")
                compose_file = CONFIG_.docker_compose
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

            docker_dict_include: Dict = {"include": includes}

            if CONFIG.attach_pangolin_site_to_compose_scope:

                add_newt_service_to_compose_scope(
                    scrape_networks=scrape_networks,
                    docker_dict_include=docker_dict_include,
                    compose_scope=compose_scope,
                    landscape_id=env["LANDSCAPE"],
                )

            docker_yaml_include = yaml.safe_dump(docker_dict_include)

            # Write docker-compose.yaml
            with open(DOCKER_COMPOSE, mode="w", encoding="utf-8") as fw:
                fw.write(docker_yaml_include)

            yield Output(docker_dict_include)

            yield AssetMaterialization(
                asset_key=context.asset_key,
                metadata={
                    "__".join(context.asset_key.path): MetadataValue.json(
                        docker_dict_include
                    ),
                    "docker_yaml": MetadataValue.md(
                        f"```yaml\n{docker_yaml_include}\n```"
                    ),
                    "includes": MetadataValue.json(includes),
                    "OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE": MetadataValue.bool(
                        CONFIG.attach_pangolin_site_to_compose_scope,
                    ),
                },
            )

        # Todo
        #  - [ ] Move to factory
        @asset(
            **ASSET_HEADER_COMPOSE,
            ins={
                "group_out_base": AssetIn(
                    AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)])
                ),
                **features,
            },
        )
        def features_in(
            context: AssetExecutionContext,
            group_out_base: dict,  # pylint: disable=redefined-outer-name
            **kwargs,
        ) -> Generator[
            Output[MutableMapping[str, List[MutableMapping[str, List]]]]
            | AssetMaterialization,
            None,
            None,
        ]:
            """ """

            context.log.info(f"{group_out_base = }")
            context.log.info(f"{kwargs = }")

            env_base = group_out_base.pop("env_base")

            config_engine = group_out_base.pop("config_engine")

            docker_config_json: pathlib.Path = group_out_base.pop("docker_config_json")

            docker_compose_yaml: MutableMapping[str, str] = {}
            docker_compose: MutableMapping[str, Any] = {}

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

            yield Output(kwargs)

            kwargs_str = json.loads(json.dumps(kwargs, default=str))

            yield AssetMaterialization(
                asset_key=context.asset_key,
                metadata={
                    "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
                    "docker_compose": MetadataValue.json(docker_compose),
                    "kwargs": MetadataValue.json(kwargs_str),
                },
            )

        @asset(
            **ASSET_HEADER_COMPOSE,
            ins={},
        )
        def cmd_extend(
            context: AssetExecutionContext,
        ) -> Generator[Output[list[Any]] | AssetMaterialization | Any, Any, None]:

            ret = []

            yield Output(ret)

            yield AssetMaterialization(
                asset_key=context.asset_key,
                metadata={
                    "__".join(context.asset_key.path): MetadataValue.json(ret),
                },
            )

        @asset(
            **ASSET_HEADER_COMPOSE,
            ins={},
        )
        def cmd_append(
            context: AssetExecutionContext,
        ) -> Generator[
            Output[dict[str, list[Any]]] | AssetMaterialization | Any, Any, None
        ]:

            ret = {"cmd": [], "exclude_from_quote": []}

            yield Output(ret)

            yield AssetMaterialization(
                asset_key=context.asset_key,
                metadata={
                    "__".join(context.asset_key.path): MetadataValue.json(ret),
                },
            )

        group_out = get_group_out(
            ASSET_HEADER=ASSET_HEADER_COMPOSE,
        )

        scrape_networks = get_scrape_networks(
            ASSET_HEADER=ASSET_HEADER_COMPOSE,
        )

        # Todo
        #  - [ ] Move to factory
        docker_compose_graph = AssetsDefinition.from_op(
            op_docker_compose_graph,
            group_name=ASSET_HEADER_COMPOSE["group_name"],
            key_prefix=ASSET_HEADER_COMPOSE["key_prefix"],
            keys_by_input_name={
                "group_out": AssetKey(
                    [*ASSET_HEADER_COMPOSE["key_prefix"], "group_out"]
                ),
                "compose_project_name": AssetKey(
                    [*ASSET_HEADER_COMPOSE["key_prefix"], "compose_project_name"]
                ),
            },
        )
