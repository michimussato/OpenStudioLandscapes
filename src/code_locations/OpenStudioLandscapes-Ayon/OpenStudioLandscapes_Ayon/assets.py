import copy
import pathlib
from typing import Generator

import git
from git.exc import GitCommandError

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

"""
dir(AssetSelection.all())
assets = AssetSelection.all(include_sources=True)
"""


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
        "AYON_PORT_HOST": "5005",
        "AYON_PORT_CONTAINER": "5000",
    }
    # @formatter:on

    env_in.update(_env)

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
def repository_ayon(
    context: AssetExecutionContext,
) -> Generator[Output[dict[str, str | None]] | AssetMaterialization, None, None]:
    repository_dict = {
        "branch": "main",
        "repository_dir": "ayon-docker",
        "repository_url": "https://github.com/ynput/ayon-docker.git",
        "repository_dir_full": None,
    }

    yield Output(repository_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(repository_dict),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
        "repository_ayon": AssetIn(
            AssetKey([KEY, "repository_ayon"]),
        ),
    },
)
def clone_repository(
    context: AssetExecutionContext,
    env: dict,
    repository_ayon: dict[str, str | None],
) -> Generator[Output[dict[str, str]] | AssetMaterialization, None, None]:

    repo_dir = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        KEY,
        "__".join(context.asset_key.path),
        "repos",
    )

    repository_dir_full = repo_dir / repository_ayon["repository_dir"]
    repository_dir_full.parent.mkdir(parents=True, exist_ok=True)

    repository_ayon["repository_dir_full"] = repository_dir_full.as_posix()
    context.log.info(repository_ayon["repository_dir_full"])

    try:
        git.Repo.clone_from(
            url=repository_ayon["repository_url"],
            to_path=repository_ayon["repository_dir_full"],
            branch=repository_ayon["branch"],
        )
    except GitCommandError as e:
        context.log.warning("Pulling from Repo (%s)" % e)
        existing_repo = git.Repo(repository_ayon["repository_dir_full"])
        origin = existing_repo.remotes.origin
        origin.pull()

    yield Output(repository_ayon)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(repository_ayon),
        },
    )


@asset(
    **asset_header,
)
def compose_networks(
    context: AssetExecutionContext,
) -> Generator[Output[dict[str, dict[str, dict[str, str]]]] | AssetMaterialization, None, None]:
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
        "clone_repository": AssetIn(
            AssetKey([KEY, "clone_repository"]),
        ),
    },
)
def compose_override(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    compose_networks: dict,  # pylint: disable=redefined-outer-name
    clone_repository: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, list[dict[str, list[str]]]]] | AssetMaterialization, None, None]:
    """"""

    parent = pathlib.Path(clone_repository["repository_dir_full"]) / "docker-compose.yml"

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
        KEY,
        "__".join(context.asset_key.path),
        "docker-compose.override.yml",
    )

    docker_compose_override.parent.mkdir(parents=True, exist_ok=True)

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
            "path_docker_yaml_override": MetadataValue.path(docker_compose_override),
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
            [KEY, "compose_override"]
        ),
        "env": AssetKey(
            [KEY, "env"]
        ),
    },
)
# Todo
#  error: /home/michael/git/repos/open-studio-landscapes/repos/ayon-docker/docker-compose.yml
#  Repo not cloned


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
