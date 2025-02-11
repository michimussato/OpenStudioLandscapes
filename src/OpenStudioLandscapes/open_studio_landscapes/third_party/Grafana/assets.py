import copy
import json
import pathlib
import importlib

import yaml

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

from OpenStudioLandscapes.open_studio_landscapes.base.assets import KEY as KEY_BASE
from OpenStudioLandscapes.open_studio_landscapes.base.ops import op_docker_compose_graph
from OpenStudioLandscapes.open_studio_landscapes.base.ops import op_group_out

GROUP = "Grafana"
KEY = "Grafana"

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
        "GRAFANA_PORT_HOST": "3030",
        "GRAFANA_PORT_CONTAINER": "3030",
    }
    # @formatter:on

    env_in.update(_env)

    env_json = pathlib.Path(
        env_in["DOT_LANDSCAPES"],
        env_in.get("LANDSCAPE", "default"),
        "third_party",
        *context.asset_key.path,
        f"{'__'.join(context.asset_key.path)}.json",
    )

    env_json.parent.mkdir(parents=True, exist_ok=True)

    with open(env_json, "w") as fw:
        json.dump(
            obj=_env.copy(),
            fp=fw,
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )

    yield Output(env_in)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_in),
            "json": MetadataValue.path(env_json),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
    },
)
def compose(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> dict:
    """ """

    docker_dict = {
        "services": {
            "grafana": {
                "container_name": "grafana",
                "hostname": "grafana",
                "domainname": env.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": "grafana/grafana",
                "networks": [
                    "repository",
                    "mongodb",
                ],
                # "environment": {
                #     "DAGSTER_HOME": env_base.get('DAGSTER_HOME'),
                #     # Todo
                #     #  - [ ] fix hard code here (from deadline-dagster .env)
                #     "DAGSTER_DEPLOYMENT": "farm",
                #     "DAGSTER_JOBS_IN": "/data/share/nfs/in",
                # },
                # "healthcheck": {
                #     "test": ["CMD", "curl", "-f", f"http://localhost:{env_base.get('DAGSTER_DEV_PORT_CONTAINER')}"],
                #     "interval": "10s",
                #     "timeout": "2s",
                #     "retries": "3",
                # },
                # "command": [
                #     "--workspace",
                #     env_base.get('DAGSTER_WORKSPACE'),
                #     "--host",
                #     env_base.get('DAGSTER_HOST'),
                #     "--port",
                #     env_base.get('DAGSTER_DEV_PORT_CONTAINER'),
                # ],
                # "volumes": [
                #     f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}",
                #     f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}",
                # ],
                "ports": [
                    f"{env.get('GRAFANA_PORT_HOST')}:{env.get('GRAFANA_PORT_CONTAINER')}",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "compose": AssetKey(
            [KEY, "compose"]
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
