import os
import copy
import pathlib
from typing import Generator, MutableMapping, Any, List

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
)
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *

from OpenStudioLandscapes.engine.common_assets.group_out import get_group_out
from OpenStudioLandscapes.engine.utils import serialize_dict


# Todo:
#  - [ ] get assets from common_assets


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "env_base": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "env_base"])),
        "DOCKER_COMPOSE": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "DOCKER_COMPOSE"])),
    },
)
def env(
    context: AssetExecutionContext,
    env_base: dict,
    DOCKER_COMPOSE: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:

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
            "COMPOSE_SCOPE": ComposeScope.DEFAULT,
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
    **ASSET_HEADER_COMPOSE,
    ins={
        "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "features_in"])),
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
    **ASSET_HEADER_COMPOSE,
    ins={
        "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "features_in"])),
    },
)
def docker_config_json(
    context: AssetExecutionContext,
    features_in: dict,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    context.log.info(features_in)

    docker_config_json = features_in.pop("docker_config_json")

    yield Output(docker_config_json)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(docker_config_json),
        },
    )


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE['key_prefix'], "features_in"])),
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


# Dynamic inputs based on the imported
# third party code locations
ins = {}
feature_ins = {}
for i in IMPORTED_FEATURES:
    # ex: module = "OpenStudioLandscapes.Ayon.definitions"
    module = i["module"]
    compose_scope = i["compose_scope"]
    if compose_scope == ComposeScope.DEFAULT:
        split = module.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))
        feature_ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "feature_out"]))


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "env"]),
        ),
        "features_in": AssetIn(
            AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "features_in"]),
        ),
    },
)
def compose(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    features_in: dict,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[MutableMapping[str, List[MutableMapping[str, List]]]] | AssetMaterialization, None, None
]:
    """ """

    features_in.pop("env_base", {})
    features_in.pop("docker_config", {})
    features_in.pop("docker_image", {})
    features_in.pop("docker_config_json", {})

    DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
    DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

    compose_files = []

    for feature, data in features_in.items():
        context.log.info(f"{features_in[feature] = }")
        compose_files.append(features_in[feature]["compose_yaml"])

    rel_paths = []
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

        rel_paths.append(rel_path.as_posix())

    docker_dict_include = {
        "include": [
            {
                "path": rel_paths,
            },
        ],
    }

    docker_yaml_include = yaml.dump(docker_dict_include)

    # Write docker-compose.yaml
    with open(DOCKER_COMPOSE, mode="w", encoding="utf-8") as fw:
        fw.write(docker_yaml_include)

    yield Output(docker_dict_include)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict_include),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml_include}\n```"),
        },
    )


@asset(
    **ASSET_HEADER_COMPOSE,
    ins={
        "group_out_base": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)])),
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
    docker_config_json: pathlib.Path = group_out_base["docker_config_json"]

    docker_compose_yaml: MutableMapping[str, str] = {}
    docker_compose: MutableMapping[str, Any] = {}

    for k, v in kwargs.items():
        # remove
        # - env_base
        # - constants_base
        # - features
        # - docker_config
        # - docker_config_json
        # from kwargs dicts
        for d in [
            "env_base",
            "constants_base",
            "features",
            "docker_config",
            "docker_config_json",
        ]:
            kwargs[k].pop(d)

        docker_compose_yaml[k] = str(kwargs[k]["compose_yaml"])
        docker_compose[k] = str(kwargs[k]["compose"])

    kwargs["env_base"] = env_base
    kwargs["docker_config"] = docker_config
    kwargs["docker_config_json"] = docker_config_json

    yield Output(kwargs)

    kwargs_serialized = copy.deepcopy(kwargs)

    serialize_dict(
        context=context,
        d=kwargs_serialized,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(kwargs_serialized),
            "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
            "docker_compose": MetadataValue.json(docker_compose),
            **metadatavalues_from_dict(
                context=context,
                d_serialized=kwargs_serialized,
            ),
        },
    )


group_out = get_group_out(
    ASSET_HEADER=ASSET_HEADER_COMPOSE,
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=ASSET_HEADER_COMPOSE["group_name"],
    key_prefix=ASSET_HEADER_COMPOSE["key_prefix"],
    keys_by_input_name={
        "group_out": AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "group_out"]),
        "compose_project_name": AssetKey([*ASSET_HEADER_COMPOSE["key_prefix"], "compose_project_name"]),
    },
)
