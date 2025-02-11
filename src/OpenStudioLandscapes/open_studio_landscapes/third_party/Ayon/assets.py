import copy
import json
import pathlib
import importlib

import yaml
from docker_compose_graph.yaml_tags.overrides import *

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
    AssetsDefinition,
)

from OpenStudioLandscapes.open_studio_landscapes.base.ops import op_group_out
from OpenStudioLandscapes.open_studio_landscapes.base.ops import op_docker_compose_graph
from OpenStudioLandscapes.open_studio_landscapes.base.assets import KEY as KEY_BASE

GROUP = "Ayon"
KEY = "Ayon"

asset_header = {"group_name": GROUP, "key_prefix": [KEY], "compute_kind": "python"}


@asset(
    **asset_header,
    deps=[
        AssetKey([KEY_BASE, "group_out"]),
    ],
)
def group_in(
    context: AssetExecutionContext,
) -> dict[str, str | dict]:

    # load asset data from external code location into memory
    # and provide it as the Output of this asset
    load_from = AssetKey([KEY_BASE, "group_out"])
    defs = importlib.import_module("OpenStudioLandscapes.open_studio_landscapes.definitions").defs
    df: dict = defs.load_asset_value(
        asset_key=load_from,
        instance=context.instance,
    )

    context.log.info(f"loaded data from Asset {load_from}: {json.dumps(df, indent=2)}")

    yield Output(df)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(df),
        },
    )


@asset(
    **asset_header,
    ins={
        "group_in": AssetIn(
            AssetKey([KEY, "group_in"]),
        ),
    },
)
def env(
    context: AssetExecutionContext,
    group_in: dict,  # pylint: disable=redefined-outer-name
) -> dict:

    env_in = copy.deepcopy(group_in["env"])

    # @formatter:off
    _env = {
        "AYON_DOCKER_COMPOSE": pathlib.Path(
            env_in["GIT_ROOT"],
            "repos",
            "ayon-docker",
            "docker-compose.yml",
        )
        .expanduser()
        .as_posix(),
        "AYON_PORT_HOST": "5005",
        "AYON_PORT_CONTAINER": "5000",
    }
    # @formatter:on

    env_in.update(_env)

    # env_json = pathlib.Path(
    #     env_in["DOT_LANDSCAPES"],
    #     env_in.get("LANDSCAPE", "default"),
    #     "third_party",
    #     *context.asset_key.path,
    #     f"{'__'.join(context.asset_key.path)}.json",
    # )

    # env_json.parent.mkdir(parents=True, exist_ok=True)
    #
    # with open(env_json, "w") as fw:
    #     json.dump(
    #         obj=_env.copy(),
    #         fp=fw,
    #         indent=2,
    #         ensure_ascii=True,
    #         sort_keys=True,
    #     )

    yield Output(env_in)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_in),
            # "json": MetadataValue.path(env_json),
        },
    )


@asset(
    **asset_header,
)
def compose_networks(
    context: AssetExecutionContext,
) -> dict:
    docker_dict = {
        "networks": {
            "mongodb": {
                "name": "network_mongodb-10-2",
            },
            "repository": {
                "name": "network_repository-10-2",
            },
            "ayon": {
                "name": "network_ayon-10-2",
            },
        },
    }

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
        "compose_networks": AssetIn(
            AssetKey([KEY, "compose_networks"]),
        ),
    },
)
def compose_override(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    compose_networks: dict,  # pylint: disable=redefined-outer-name
) -> dict:
    """"""

    parent = pathlib.Path(env.get("AYON_DOCKER_COMPOSE"))

    docker_dict_override = {
        "networks": compose_networks.get("networks", []),
        "services": {
            "postgres": {
                "container_name": "ayon-postgres",
                "hostname": "ayon-postgres",
                "domainname": env.get("ROOT_DOMAIN"),
                "volumes": [
                    f"/etc/localtime:/etc/localtime:ro",
                    f"{env.get('NFS_ENTRY_POINT')}/databases/ayon/postgresql/data:/var/lib/postgresql/data",
                ],
                "networks": list(compose_networks.get("networks", {}).keys()),
            },
            "redis": {
                "container_name": "ayon-redis",
                "hostname": "ayon-redis",
                "domainname": env.get("ROOT_DOMAIN"),
                "networks": [
                    "mongodb",
                    "repository",
                ],
            },
            "server": {
                "container_name": "ayon-server",
                "hostname": "ayon-server",
                "domainname": env.get("ROOT_DOMAIN"),
                # Todo:
                #  - [ ] Need to find out whether `ports` Override
                #  also overrides the exports in the source ayon-docker-compose.yml
                #  "exports": OverrideArray([]),
                "ports": OverrideArray(
                    [
                        f"{env.get('AYON_PORT_HOST')}:{env.get('AYON_PORT_CONTAINER')}",
                    ]
                ),
                "networks": [
                    "mongodb",
                    "repository",
                ],
            },
        },
    }

    docker_compose_override = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        "docker_compose",
        *context.asset_key.path,
        "docker-compose.override.yml",
    )

    docker_yaml_override: str = yaml.dump(docker_dict_override)

    with open(docker_compose_override, "w") as fw:
        fw.write(docker_yaml_override)

    # Write compose override to disk here to be able to reference
    # it in the following step.
    # It seems that it's necessary to apply overrides in
    # include: path

    docker_dict_include ={
        "include": [
            {
                "path": [
                    parent.as_posix(),
                    docker_compose_override.as_posix(),
                ],
            },
        ],
    }

    yield Output(docker_dict_include)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict_include),
            "docker_yaml_override": MetadataValue.md(f"```yaml\n{docker_yaml_override}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "compose": AssetKey(
            [KEY, "compose_override"]
        ),
        "env": AssetKey(
            [KEY, "env"]
        ),
    },
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "group_out": AssetKey(
            [KEY, "group_out"]
        ),
    },
)
