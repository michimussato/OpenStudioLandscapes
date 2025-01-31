import pathlib
import yaml
import shutil
import json

from Deadline.open_studio_landscapes.utils import *

from docker_graph.yaml_tags.overrides import *

from dagster import (
    AssetIn,
    AssetKey,
    asset,
    AssetExecutionContext,
    Output,
    AssetMaterialization,
    MetadataValue
)

from Deadline.open_studio_landscapes.assets import KEY as KEY_BASE


GROUP = "Ayon"
KEY = "Ayon"

asset_header = {
    "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python"
}


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
        env: dict,
) -> dict:

    # @formatter:off
    _env = {
        "AYON_DOCKER_COMPOSE": pathlib.Path(
            env["GIT_ROOT"],
            "repos",
            "ayon-docker",
            "docker-compose.yml",
        ).expanduser().as_posix(),
        "AYON_PORT_HOST": "5005",
        "AYON_PORT_CONTAINER": "5000",
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
def compose_override(
        context: AssetExecutionContext,
        env: dict,
) -> dict[str, list[str]]:
    """
    """

    parent = pathlib.Path(env.get("AYON_DOCKER_COMPOSE"))

    docker_dict = {
        "services": {
            "postgres": {
                "container_name": "ayon-postgres",
                "hostname": "ayon-postgres",
                "domainname": env.get("ROOT_DOMAIN"),
                "volumes": [
                    f"/etc/localtime:/etc/localtime:ro",
                    f"{env.get('NFS_ENTRY_POINT')}/databases/ayon/postgresql/data:/var/lib/postgresql/data",
                ],
                "networks": [
                    "mongodb",
                    "repository",
                ],
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
                "ports": OverrideArray([
                    f"{env.get('AYON_PORT_HOST')}:{env.get('AYON_PORT_CONTAINER')}",
                ]),
                "networks": [
                    "mongodb",
                    "repository",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    docker_compose_override = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        "docker_compose",
        *context.asset_key.path,
        "docker-compose.override.yml",
    )

    docker_compose_override.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose_override, "w") as fw:
        fw.write(docker_yaml)

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        parent.as_posix(),
        "--project-name",
        "__".join(context.asset_key.path),
        "up",
        "--remove-orphans",
    ]

    ret = {
        "path": [
            parent.as_posix(),
            docker_compose_override.as_posix(),
        ],
    }

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
            "cmd_docker_compose_up": MetadataValue.path(cmd_list_to_str(cmd_docker_compose_up)),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )
