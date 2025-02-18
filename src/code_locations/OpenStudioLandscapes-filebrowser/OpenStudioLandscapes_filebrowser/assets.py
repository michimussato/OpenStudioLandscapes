import copy
import pathlib
from typing import Generator

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

GROUP = "filebrowser"
KEY = "filebrowser"

asset_header = {"group_name": GROUP, "key_prefix": [KEY], "compute_kind": "python"}


@asset(
    **asset_header,
    ins={
        "group_in": AssetIn(
            AssetKey([KEY_BASE, "group_out"])
        ),
    },
)
def env(
    context: AssetExecutionContext,
    group_in: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    env_in = copy.deepcopy(group_in["env"])

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

    yield Output(env_in)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_in),
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
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

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
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP,
    tags_by_output_name={
        "group_out": {
            "group_out": "third_party",
        },
    },
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
