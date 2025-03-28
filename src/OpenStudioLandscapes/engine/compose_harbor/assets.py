import pathlib
import shlex
import shutil
from typing import Generator
import copy

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

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *


@asset(
    **ASSET_HEADER_HARBOR,
    ins={
        "group_in": AssetIn(
            AssetKey([*KEY_BASE, "group_out"])
        ),
    },
    deps=[
        AssetKey([*ASSET_HEADER_HARBOR['key_prefix'], f"constants_{ASSET_HEADER_HARBOR['group_name']}"])
    ],
)
def env(
    context: AssetExecutionContext,
    group_in: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    env_in = copy.deepcopy(group_in["env"])

    env_in.update(ENVIRONMENT_HARBOR)

    env_in.update(
        {
            "COMPOSE_SCOPE": ComposeScope.HARBOR,
        },
    )

    yield Output(env_in)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_in),
            "ENVIRONMENT_HARBOR": MetadataValue.json(ENVIRONMENT_HARBOR),
        },
    )


@asset(
    **ASSET_HEADER_HARBOR,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_BASE, "env"]),
        ),
    },
)
def harbor_root(
        context: AssetExecutionContext,
        env: dict,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    tarball_dir = pathlib.Path(
        env["DOT_LANDSCAPES"],
        ".harbor",
    )

    tarball_dir.mkdir(parents=True, exist_ok=True)

    yield Output(tarball_dir)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(tarball_dir),
        },
    )


@asset(
    **ASSET_HEADER_HARBOR,
    ins={
        "write_yaml": AssetIn(
            AssetKey([*KEY_HARBOR, "write_yaml"]),
        ),
    },
)
def prepare(
        context: AssetExecutionContext,
        write_yaml: pathlib.Path,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
    """Is Harbor installed in the designated destination so that
    we can write a docker compose file to that destination?"""

    cmd_prepare = [
        shutil.which("sudo"),
        shutil.which("bash"),
        pathlib.Path(write_yaml.parent / "prepare").as_posix(),
    ]

    # MUST run as root apparently
    # cmd_chmod = [
    #     shutil.which("sudo"),
    #     shutil.which("chmod"),
    #     "-R",
    #     "a+r",
    #     pathlib.Path(get_harbor).as_posix(),
    # ]

    if not pathlib.Path(write_yaml).exists():
        raise FileNotFoundError(f"Run prepare first: '{shlex.join(cmd_prepare)}'")

    docker_compose = write_yaml.parent / "docker-compose.yml"

    if not pathlib.Path(docker_compose).exists():
        raise FileNotFoundError(f"Run prepare first: '{shlex.join(cmd_prepare)}'")

    yield Output(docker_compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "harbor_yml": MetadataValue.path(write_yaml),
            "docker_compose_yml": MetadataValue.path(docker_compose),
        },
    )


@asset(
    **ASSET_HEADER_HARBOR,
    ins={
        "harbor_root": AssetIn(
            AssetKey([*KEY_HARBOR, "harbor_root"]),
        ),
    },
    description="Returns the docker-compose path."
)
def write_yaml(
        context: AssetExecutionContext,
        harbor_root: pathlib.Path,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    yaml_out = harbor_root / "bin" / "harbor.yml"
    registry_data_root = harbor_root / "data"

    harbor_dict = {
        'hostname': 'harbor.farm.evil',
        'http': {'port': 80},
        'harbor_admin_password': 'Harbor12345',
        'database': {
            'password': 'root123',
            'max_idle_conns': 100,
            'max_open_conns': 900,
            'conn_max_idle_time': 0
        },
        'data_volume': registry_data_root.as_posix(),
        'trivy': {
            'ignore_unfixed': False,
            'skip_update': False,
            'skip_java_db_update': False,
            'offline_scan': False,
            'security_check': 'vuln',
            'insecure': False,
            'timeout': '5m0s'
        },
        'jobservice': {
            'max_job_workers': 10,
            'job_loggers': ['STD_OUTPUT', 'FILE'],
            'logger_sweeper_duration': 1
        },
        'notification': {
            'webhook_job_max_retry': 3,
            'webhook_job_http_client_timeout': 3
        },
        'log': {
            'level': 'info',
            'local': {
                'rotate_count': 50,
                'rotate_size': '200M',
                'location': '/var/log/harbor'
            }
        },
        '_version': '2.12.0',
        'proxy': {
            'http_proxy': None,
            'https_proxy': None,
            'no_proxy': None,
            'components': ['core', 'jobservice', 'trivy']
        },
        'upload_purging': {
            'enabled': True,
            'age': '168h',
            'interval': '24h',
            'dryrun': False
        },
        'cache': {
            'enabled': False,
            'expire_hours': 24
        }
    }

    harbor_yml: str = yaml.dump(harbor_dict)

    with open(yaml_out, "w") as fw:
        fw.write(harbor_yml)

    yield Output(yaml_out)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(yaml_out),
            "harbor_yml": MetadataValue.md(f"```yaml\n{harbor_yml}\n```"),
        },
    )


@asset(
    **ASSET_HEADER_HARBOR,
    ins={
        "prepare": AssetIn(
            AssetKey([*KEY_HARBOR, "prepare"]),
        ),
        # "env": AssetIn(
        #     AssetKey([*KEY_HARBOR, "env"]),
        # ),
    },
)
def compose(
        context: AssetExecutionContext,
        prepare: pathlib.Path,
        # env: dict,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    with open(prepare, "r") as fw:
        docker_compose_yaml = fw.read()
        docker_compose_dict = yaml.safe_load(docker_compose_yaml)

    # compose_project_name = f"{env.get('LANDSCAPE', 'default').replace('.', '-')}-{env['COMPOSE_SCOPE']}"
    compose_project_name = "openstudiolandscapes-harbor"

    cmd_docker_compose_up = [
        shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        prepare.as_posix(),
        "--project-name",
        compose_project_name,
        "up",
        "--remove-orphans",
    ]

    cmd_docker_compose_down = [
        shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        prepare.as_posix(),
        "--project-name",
        compose_project_name,
        "down",
    ]

    yield Output(docker_compose_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_compose_dict),
            "cmd_docker_compose_up": MetadataValue.path(
                " ".join(
                    shlex.quote(s) if not s in ["&&", ";"] else s
                    for s in cmd_docker_compose_up
                )
            ),
            "cmd_docker_compose_down": MetadataValue.path(
                " ".join(
                    shlex.quote(s) if not s in ["&&", ";"] else s
                    for s in cmd_docker_compose_down
                )
            ),
            "docker_compose_yaml": MetadataValue.md(f"```yaml\n{docker_compose_yaml}\n```"),
        },
    )


# # Todo
# #  - [ ] cmd_docker_compose_up creates an additional docker-compose.yaml which
# #        is undesirable in this instance as it creates the wrong paths while docker compose up
# #        ignore for now
# group_out = AssetsDefinition.from_op(
#     op_group_out,
#     can_subset=True,
#     group_name=GROUP_HARBOR,
#     tags_by_output_name={
#         "group_out": {
#             "group_out": "third_party",
#         },
#     },
#     key_prefix=KEY_HARBOR,
#     keys_by_input_name={
#         "compose": AssetKey(
#             [*KEY_HARBOR, "compose"]
#         ),
#         "env": AssetKey(
#             [*KEY_HARBOR, "env"]
#         ),
#         "group_in": AssetKey(
#             [*KEY_BASE, "group_out"]
#         ),
#     },
# )
#
#
# docker_compose_graph = AssetsDefinition.from_op(
#     op_docker_compose_graph,
#     group_name=GROUP_HARBOR,
#     key_prefix=KEY_HARBOR,
#     keys_by_input_name={
#         "group_out": AssetKey(
#             [*KEY_HARBOR, "group_out"]
#         ),
#         "compose_project_name": AssetKey(
#             [*KEY_HARBOR, "compose_project_name"]
#         ),
#     },
# )
