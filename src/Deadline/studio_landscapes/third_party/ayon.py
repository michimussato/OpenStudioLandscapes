import pathlib
import yaml
import shutil

from Deadline.studio_landscapes.utils import *

from docker_graph.yaml_tags.overrides import *

from dagster import (
    AssetIn,
    asset,
    AssetExecutionContext,
    Output,
    AssetMaterialization,
    MetadataValue
)


@asset(
    group_name="Ayon",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
    },
)
def compose_ayon_override(
        context: AssetExecutionContext,
        env_base: dict,
) -> dict[str, list[str]]:
    """
    """

    parent = pathlib.Path(env_base.get("AYON_DOCKER_COMPOSE"))

    docker_dict = {
        "services": {
            "postgres": {
                "container_name": "ayon-postgres",
                "hostname": "ayon-postgres",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "volumes": [
                    f"/etc/localtime:/etc/localtime:ro",
                    f"{env_base.get('NFS_ENTRY_POINT')}/databases/ayon/postgresql/data:/var/lib/postgresql/data",
                ],
                "networks": [
                    "mongodb",
                    "repository",
                ],
            },
            "redis": {
                "container_name": "ayon-redis",
                "hostname": "ayon-redis",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "networks": [
                    "mongodb",
                    "repository",
                ],
            },
            "server": {
                "container_name": "ayon-server",
                "hostname": "ayon-server",
                "domainname": env_base.get("ROOT_DOMAIN"),
                # "exports": OverrideArray([]),
                "ports": OverrideArray([
                    f"{env_base.get('AYON_PORT_HOST')}:{env_base.get('AYON_PORT_CONTAINER')}",
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
        env_base["DOT_LANDSCAPES"],
        env_base.get("LANDSCAPE", "default"),
        "docker_compose",
        context.asset_key.path[-1],
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
        context.asset_key.path[-1],
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
            context.asset_key.path[-1]: MetadataValue.json(ret),
            "cmd_docker_compose_up": MetadataValue.path(cmd_list_to_str(cmd_docker_compose_up)),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
        },
    )
