import json
import pathlib

import yaml
from python_on_whales import docker

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)
from OpenStudioLandscapes.open_studio_landscapes.assets import KEY as KEY_BASE
from OpenStudioLandscapes.open_studio_landscapes.constants import *
from OpenStudioLandscapes.open_studio_landscapes.utils import *

GROUP = "Grafana"
KEY = "Grafana"

asset_header = {"group_name": GROUP, "key_prefix": [KEY], "compute_kind": "python"}


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY_BASE, "env"]),
        ),
    },
)
def env(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> dict:

    # @formatter:off
    _env = {
        "GRAFANA_PORT_HOST": "3030",
        "GRAFANA_PORT_CONTAINER": "3030",
    }
    # @formatter:on

    env.update(_env)

    env_json = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
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

    yield Output(env)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env),
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
            "docker_dict": MetadataValue.md(
                f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
            ),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env": MetadataValue.json(env),
        },
    )
