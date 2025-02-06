import copy
import json
import pathlib

import yaml

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

GROUP = "filebrowser"
KEY = "filebrowser"

asset_header = {"group_name": GROUP, "key_prefix": [KEY], "compute_kind": "python"}


@asset(
    **asset_header,
    ins={
        "group_out_base": AssetIn(
            AssetKey([KEY_BASE, "group_out"]),
        ),
    },
)
def env(
    context: AssetExecutionContext,
    group_out_base: dict,  # pylint: disable=redefined-outer-name
) -> dict:

    env_in = copy.deepcopy(group_out_base["env"])

    # @formatter:off
    _env = {
        "FILEBROWSER_PORT_HOST": "8080",
        "FILEBROWSER_PORT_CONTAINER": "80",
        "FILEBROWSER_DB": pathlib.Path(
            env_in["CONFIGS_ROOT"],
            "filebrowser",
            "db",
            "filebrowser.db",
        )
        .expanduser()
        .as_posix(),
        "FILEBROWSER_JSON": pathlib.Path(
            env_in["CONFIGS_ROOT"],
            "filebrowser",
            "json",
            "filebrowser.json",
        )
        .expanduser()
        .as_posix(),
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

    image = "filebrowser/filebrowser"

    volumes = [
        f"{env.get('FILEBROWSER_DB')}:/filebrowser.db",
        f"{env.get('FILEBROWSER_JSON')}:/.filebrowser.json",
        f"{env.get('NFS_ENTRY_POINT')}:{env.get('NFS_ENTRY_POINT')}:ro",
        f"{env.get('NFS_ENTRY_POINT')}:{env.get('NFS_ENTRY_POINT_LNS')}:ro",
    ]

    docker_dict = {
        "services": {
            "filebrowser": {
                "image": image,
                "container_name": "filebrowser-10-2",
                "hostname": "filebrowser-10-2",
                "domainname": env.get("ROOT_DOMAIN"),
                "restart": "always",
                "networks": [
                    "repository",
                ],
                "ports": [
                    f"{env.get('FILEBROWSER_PORT_HOST')}:{env.get('FILEBROWSER_PORT_CONTAINER')}",
                ],
                "volumes": volumes,
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
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **asset_header,
    ins={
        "compose": AssetIn(
            AssetKey([KEY, "compose"]),
        ),
    },
)
def group_out(
    context: AssetExecutionContext,
    compose: dict,  # pylint: disable=redefined-outer-name
) -> dict:

    out_dict: dict = dict()

    out_dict["docker_compose"] = copy.deepcopy(compose)

    yield Output(out_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(out_dict),
        },
    )
