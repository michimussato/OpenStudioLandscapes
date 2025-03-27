import pathlib
import shlex
import shutil
from typing import Generator
import requests
import tarfile

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
from OpenStudioLandscapes.engine.utils import *


# @asset(
#     **ASSET_HEADER_HARBOR,
#     ins={
#         "git_root": AssetIn(AssetKey([*KEY_BASE, "git_root"])),
#         "secrets": AssetIn(AssetKey([*KEY_BASE, "secrets"])),
#         "landscape_id": AssetIn(AssetKey([*KEY_BASE, "landscape_id"])),
#         "dot_landscapes": AssetIn(AssetKey([*KEY_BASE, "dot_landscapes"])),
#         "nfs": AssetIn(AssetKey([*KEY_BASE, "nfs"])),
#     },
#     deps=[
#         AssetKey(
#             [
#                 *ASSET_HEADER_HARBOR["key_prefix"],
#                 f"constants_{ASSET_HEADER_HARBOR['group_name']}",
#             ]
#         )
#     ],
# )
# def env(
#         context: AssetExecutionContext,
#         git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
#         secrets: dict,  # pylint: disable=redefined-outer-name
#         landscape_id: dict,  # pylint: disable=redefined-outer-name
#         dot_landscapes: pathlib.Path,  # pylint: disable=redefined-outer-name
#         nfs: dict,  # pylint: disable=redefined-outer-name
# ) -> Generator[Output[dict] | AssetMaterialization, None, None]:
#     # @formatter:off
#     # Todo
#     #  - [ ] Move to constants.py
#     ENVIRONMENT_BASE: dict = {
#         "GIT_ROOT": git_root.as_posix(),
#         # Todo
#         #  - [ ] Move CONFIGS_ROOT to individual modules
#         "CONFIGS_ROOT": pathlib.Path(
#             git_root,
#             "configs",
#         ).as_posix(),
#         "DOT_LANDSCAPES": dot_landscapes.as_posix(),
#         "AUTHOR": "michimussato@gmail.com",
#         "CREATED_BY": str(getpass.getuser()),
#         "CREATED_ON": str(socket.gethostname()),
#         "CREATED_AT": str(datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")),
#         "TIMEZONE": "Europe/Zurich",
#         # "IMAGE_PREFIX": "michimussato",
#         "DEFAULT_CONFIG_DBPATH": "/data/configdb",
#         "ROOT_DOMAIN": "farm.evil",
#         # https://vfxplatform.com/
#         "PYTHON_MAJ": "3",
#         "PYTHON_MIN": "11",
#         "PYTHON_PAT": "11",
#     }
#
#     ENVIRONMENT_BASE.update(secrets)
#     ENVIRONMENT_BASE.update(landscape_id)
#     ENVIRONMENT_BASE.update(nfs)
#     # @formatter:on
#
#     yield Output(ENVIRONMENT_BASE)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(ENVIRONMENT_BASE),
#         },
#     )


@asset(
    **ASSET_HEADER_HARBOR,
    ins={
        "env": AssetIn(
            AssetKey([*KEY_BASE, "env"]),
        ),
    },
)
def get_harbor(
        context: AssetExecutionContext,
        env: dict,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
    urls = {
        "harbor_online": "https://github.com/goharbor/harbor/releases/download/v2.12.2/harbor-online-installer-v2.12.2.tgz",
        "harbor_offline": "https://github.com/goharbor/harbor/releases/download/v2.12.2/harbor-offline-installer-v2.12.2.tgz",
    }

    tarball_dir = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{GROUP_HARBOR}__{'__'.join(KEY_HARBOR)}",
        "__".join(context.asset_key.path),
        "tarball",
    )

    extract_dir = tarball_dir.parent

    url = urls["harbor_online"]
    filename = "harbor-installer.tgz"

    tarball_dir.mkdir(parents=True, exist_ok=True)

    with requests.get(url, stream=True) as response:
        with open(tarball_dir / filename, mode="wb") as fw:
            for chunk in response.iter_content(chunk_size=10 * 1024):
                fw.write(chunk)

    with tarfile.open(tarball_dir / filename) as tar:
        tar.extractall(extract_dir)

    yield Output(extract_dir / "harbor")

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(extract_dir / "harbor"),
        },
    )


@asset(
    **ASSET_HEADER_HARBOR,
    ins={},
)
def registry_data_root(
        context: AssetExecutionContext,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    registry_root = pathlib.Path(
        get_git_root(__file__),
        ".registry",
        "harbor",
    )

    registry_root.mkdir(parents=True, exist_ok=True)

    yield Output(registry_root)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(registry_root),
        },
    )


@asset(
    **ASSET_HEADER_HARBOR,
    ins={
        # "env": AssetIn(
        #     AssetKey([*KEY_BASE, "env"]),
        # ),
        "registry_data_root": AssetIn(
            AssetKey([*KEY_HARBOR, "registry_data_root"]),
        ),
        "get_harbor": AssetIn(
            AssetKey([*KEY_HARBOR, "get_harbor"]),
        ),
    },
)
def write_yaml(
        context: AssetExecutionContext,
        # env: dict,
        registry_data_root: pathlib.Path,
        get_harbor: pathlib.Path,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    yaml_out = get_harbor / "harbor.yml"

    harbor_dict = {
        'hostname': '192.168.1.164',
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
        "get_harbor": AssetIn(
            AssetKey([*KEY_HARBOR, "get_harbor"]),
        ),
    },
    deps=[
        AssetKey([*KEY_HARBOR, "write_yaml"]),
    ]
)
def docker_compose(
        context: AssetExecutionContext,
        get_harbor: pathlib.Path,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    cmd_cwd = [
        "cd",
        get_harbor.as_posix(),
    ]

    cmd_install = [
        shutil.which("sudo"),
        "./install.sh",
    ]

    # This docker-compse was dynamically created by the
    # Harbor install script (./install.sh)
    docker_compose = get_harbor / "docker-compose.yml"

    with open(docker_compose, "r") as fw:
        docker_compose_yaml = fw.read()
        docker_compose_dict = yaml.safe_load(docker_compose_yaml)

    cmd_docker_compose_up = [
        shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        "harbor",
        "up",
        "--remove-orphans",
    ]

    cmd_docker_compose_down = [
        shutil.which("sudo"),
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        "harbor",
        "down",
    ]

    yield Output(docker_compose_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_compose_dict),
            "docker_compose_yaml": MetadataValue.md(f"```yaml\n{docker_compose_yaml}\n```"),
            "01_cmd_cwd": MetadataValue.path(shlex.join(cmd_cwd)),
            "02_cmd_install": MetadataValue.path(shlex.join(cmd_install)),
            "03_cmd_docker_compose_up": MetadataValue.path(
                " ".join(
                    shlex.quote(s) if not s in ["&&", ";"] else s
                    for s in cmd_docker_compose_up
                )
            ),
            "04_cmd_docker_compose_down": MetadataValue.path(
                " ".join(
                    shlex.quote(s) if not s in ["&&", ";"] else s
                    for s in cmd_docker_compose_down
                )
            ),
        },
    )
