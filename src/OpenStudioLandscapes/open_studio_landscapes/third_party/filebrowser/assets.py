import copy
import json
import pathlib
import importlib
import shlex
import shutil

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

GROUP = "filebrowser"
KEY = "filebrowser"

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
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            # Todo: "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


@asset(
    **asset_header,
    ins={
        "compose": AssetIn(
            AssetKey([KEY, "compose"]),
        ),
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
    },
)
def group_out(
    context: AssetExecutionContext,
    compose: dict,  # pylint: disable=redefined-outer-name
    env: dict,  # pylint: disable=redefined-outer-name
) -> pathlib.Path:

    docker_yaml = yaml.dump(compose)

    docker_compose = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        KEY,
        "docker_compose",
        "__".join(context.asset_key.path),
        "docker-compose.yml",
    )

    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}"

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "up",
        "--remove-orphans",
    ]

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "down",
        "--remove-orphans",
    ]

    yield Output(docker_compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
            "cmd_docker_compose_up": MetadataValue.path(
                " ".join(shlex.quote(s) for s in cmd_docker_compose_up)
            ),
            "cmd_docker_compose_down": MetadataValue.path(
                " ".join(shlex.quote(s) for s in cmd_docker_compose_down)
            ),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )
