import copy
import os
import pathlib
from typing import Generator, List, MutableMapping, Any

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
)

from OpenStudioLandscapes.engine.base.ops import (
    op_docker_compose_graph,
    op_group_out,
)
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *


# Dynamic inputs based on the imported
# third party code locations
ins = {}
feature_ins = {}
for i in IMPORTED_FEATURES:
    # ex: module = "OpenStudioLandscapes.Ayon.definitions"
    module = i["module"]
    compose_scope = i["compose_scope"]
    if compose_scope == ComposeScope.LICENSE_SERVER:
        split = module.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))
        feature_ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "feature_out"]))


if bool(ins):
    @asset(
        **ASSET_HEADER_COMPOSE_LICENSE_SERVER,
        ins={
        "env_base": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER['key_prefix'], "env_base"])),
        "DOCKER_COMPOSE": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER['key_prefix'], "DOCKER_COMPOSE"])),
        },
        deps=[
            AssetKey(
                [*ASSET_HEADER_COMPOSE_LICENSE_SERVER['key_prefix'], "constants_compose_license_server"]
            )
        ],
    )
    def env(
        context: AssetExecutionContext,
    env_base: dict,
    DOCKER_COMPOSE: pathlib.Path,  # pylint: disable=redefined-outer-name
    ) -> Generator[Output[dict] | AssetMaterialization, None, None]:

        env_in = copy.deepcopy(env_base)

        env_in.update(
            expand_dict_vars(
                dict_to_expand={
                    "DOCKER_COMPOSE": DOCKER_COMPOSE.as_posix()
                },
                kv=env_in,
            )
        )

        env_in.update(
            {
                "COMPOSE_SCOPE": ComposeScope.LICENSE_SERVER,
            }
        )

        yield Output(env_in)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(env_in),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_LICENSE_SERVER,
        ins={
            "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER['key_prefix'], "features_in"])),
        },
    )
    def env_base(
        context: AssetExecutionContext,
        features_in: dict,
    ) -> Generator[Output[dict] | AssetMaterialization, None, None]:

        context.log.info(features_in)

        _env_base = features_in.pop("env_base", {})

        yield Output(_env_base)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(_env_base),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_LICENSE_SERVER,
        ins={
            "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER['key_prefix'], "features_in"])),
        },
    )
    def docker_config(
        context: AssetExecutionContext,
        features_in: dict,
    ) -> Generator[Output[DockerConfig] | AssetMaterialization, None, None]:

        context.log.info(features_in)

        _docker_config: DockerConfig = features_in.pop("docker_config")
        context.log.info(_docker_config)

        yield Output(_docker_config)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                _docker_config.name: MetadataValue.json(_docker_config.value),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_LICENSE_SERVER,
        ins={
            "env": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"], "env"]),
            ),
            **ins,
        },
    )
    def compose(
        context: AssetExecutionContext,
        env: dict,  # pylint: disable=redefined-outer-name
        **kwargs,
    ) -> Generator[
        Output[dict[str, list[dict[str, list]]]] | AssetMaterialization, None, None
    ]:
        """ """

        context.log.info(kwargs)

        _group_in = []

        docker_compose = pathlib.PurePosixPath(
            env["DOT_LANDSCAPES"],
            env.get("LANDSCAPE", "default"),
            f"{ASSET_HEADER_COMPOSE_LICENSE_SERVER['group_name']}__{'__'.join(ASSET_HEADER_COMPOSE_LICENSE_SERVER['key_prefix'])}",
            "__".join(context.asset_key.path),
            "docker_compose",
            "docker-compose.yml",
        )

        context.log.info(docker_compose)
        context.log.info(type(docker_compose))

        for v in kwargs.values():
            _rel_path = os.path.relpath(
                path=v.as_posix(),
                start=docker_compose.parent.as_posix(),
            )
            rel_path = pathlib.Path(_rel_path)

            _group_in.append(rel_path)

        docker_dict = {
            "include": [{"path": [i.as_posix()]} for i in _group_in],
        }

        docker_yaml = yaml.dump(docker_dict)

        yield Output(docker_dict)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
                "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_LICENSE_SERVER,
        ins={
            "group_out_base": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out"])),
            **feature_ins,
        },
    )
    def features_in(
        context: AssetExecutionContext,
        group_out_base: dict,  # pylint: disable=redefined-outer-name
        **kwargs,
    ) -> Generator[
        Output[MutableMapping[str, List[MutableMapping[str, List]]]] | AssetMaterialization, None, None
    ]:
        """ """

        context.log.info(kwargs)

        env_base = group_out_base["env_base"]
        docker_config: DockerConfig = group_out_base["docker_config"]

        docker_compose_yaml: MutableMapping[str, str] = {}
        docker_compose: MutableMapping[str, Any] = {}

        for k, v in kwargs.items():
            # remove
            # - env_base
            # - constants_base
            # - features
            # - docker_config
            # from kwargs dicts
            for d in [
                "env_base",
                "constants_base",
                "features",
                "docker_config",
            ]:
                kwargs[k].pop(d)

            docker_compose_yaml[k] = str(kwargs[k]["compose_yaml"])
            docker_compose[k] = str(kwargs[k]["compose"])

        kwargs["env_base"] = env_base
        kwargs["docker_config"] = docker_config

        metadata = {}

        out_ = copy.deepcopy(kwargs)

        # JSON cannot serialize certain types
        # out of the box. This makes sure that
        # MetadataValue.json receives only
        # serializable input.
        def _serialize(d):
            for k_, v_ in d.items():
                if isinstance(v_, MutableMapping):
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

        yield Output(kwargs)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(out_),
                "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
                "docker_compose": MetadataValue.json(docker_compose),
                **metadata,
            },
        )


    group_out = AssetsDefinition.from_op(
        op_group_out,
        # Todo:
        #  - [ ] Better to use False here?
        can_subset=False,
        group_name=ASSET_HEADER_COMPOSE_LICENSE_SERVER["group_name"],
        key_prefix=ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"],
        keys_by_input_name={
            "compose": AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"], "compose"]),
            "env": AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"], "env"]),
            "docker_config": AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"], "docker_config"]),
        },
    )


    docker_compose_graph = AssetsDefinition.from_op(
        op_docker_compose_graph,
        group_name=ASSET_HEADER_COMPOSE_LICENSE_SERVER["group_name"],
        key_prefix=ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"],
        keys_by_input_name={
            "group_out": AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"], "group_out"]),
            "compose_project_name": AssetKey([*ASSET_HEADER_COMPOSE_LICENSE_SERVER["key_prefix"], "compose_project_name"]),
        },
    )
