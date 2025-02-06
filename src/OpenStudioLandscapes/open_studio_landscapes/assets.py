import copy
import getpass
import json
import pathlib
import yaml
import shutil
import socket
import textwrap
import time
import urllib.parse
import uuid
from datetime import datetime
from pathlib import Path
from collections import ChainMap
from functools import reduce
import shlex

from typing import Any, Generator

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

from docker_compose_graph.utils import *

from OpenStudioLandscapes.open_studio_landscapes.constants import *
from OpenStudioLandscapes.open_studio_landscapes.utils import *

# GROUP = ""
KEY = "Base"

asset_header = {
    # "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python",
}


@asset(
    **asset_header,
    group_name="Environment",
)
def git_root(
    context: AssetExecutionContext,
) -> Generator[Output[Path] | AssetMaterialization | Any, Any, None]:

    _git_root = get_git_root()

    yield Output(_git_root)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_git_root),
        },
    )


@asset(
    **asset_header,
    group_name="Environment",
)
def landscape_id(
    context: AssetExecutionContext,
) -> Generator[Output[dict[str, str]] | AssetMaterialization | Any, Any, None]:

    now = datetime.now()

    landscape_stamp = {
        "LANDSCAPE": f"{datetime.strftime(now, '%Y-%m-%d_%H-%M-%S')}__{uuid.uuid4().hex}",
    }

    yield Output(landscape_stamp)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(landscape_stamp),
        },
    )


@asset(
    **asset_header,
    group_name="Environment",
)
def secrets(
    context: AssetExecutionContext,
) -> Generator[Output[dict | Any] | AssetMaterialization | Any, Any, None]:
    try:
        from __SECRET__.secrets import secrets as _secrets
    except ModuleNotFoundError:
        context.log.exception("Failed to import secrets from __SECRET__.secrets")
        _secrets: dict = {}

    yield Output(_secrets)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_secrets),
        },
    )


@asset(
    **asset_header,
    group_name="Environment",
    ins={
        "git_root": AssetIn(
            AssetKey([KEY, "git_root"]),
        ),
    },
)
def dot_landscapes(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path] | AssetMaterialization | Any, Any, None]:

    dot_landscapes = git_root / ".landscapes"
    dot_landscapes.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield Output(dot_landscapes)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(dot_landscapes),
        },
    )


@asset(
    **asset_header,
    group_name="Environment",
    ins={
        "git_root": AssetIn(AssetKey([KEY, "git_root"])),
    },
)
def dot_installers(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path] | AssetMaterialization | Any, Any, None]:

    dot_installers = git_root / ".installers"
    dot_installers.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield Output(dot_installers)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(dot_installers),
        },
    )


@asset(
    **asset_header,
    group_name="Environment",
    ins={
        "git_root": AssetIn(AssetKey([KEY, "git_root"])),
        "secrets": AssetIn(AssetKey([KEY, "secrets"])),
        "landscape_id": AssetIn(AssetKey([KEY, "landscape_id"])),
        "dot_landscapes": AssetIn(AssetKey([KEY, "dot_landscapes"])),
        "dot_installers": AssetIn(AssetKey([KEY, "dot_installers"])),
        "nfs": AssetIn(AssetKey([KEY, "nfs"])),
    },
)
def env(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
    secrets: dict,  # pylint: disable=redefined-outer-name
    landscape_id: dict,  # pylint: disable=redefined-outer-name
    dot_landscapes: pathlib.Path,  # pylint: disable=redefined-outer-name
    dot_installers: pathlib.Path,  # pylint: disable=redefined-outer-name
    nfs: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization | Any, Any, None]:
    # @formatter:off

    _env: dict = {
        "GIT_ROOT": git_root.as_posix(),
        "CONFIGS_ROOT": pathlib.Path(
            git_root,
            "configs",
        ).as_posix(),
        "DOT_LANDSCAPES": dot_landscapes.as_posix(),
        "DOT_INSTALLERS": dot_installers.as_posix(),
        "AUTHOR": "michimussato@gmail.com",
        "CREATED_BY": str(getpass.getuser()),
        "CREATED_ON": str(socket.gethostname()),
        "CREATED_AT": str(datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")),
        "TIMEZONE": "Europe/Zurich",
        "IMAGE_PREFIX": "michimussato",
        "MONGO_EXPRESS_PORT_HOST": "8181",
        "MONGO_EXPRESS_PORT_CONTAINER": "8081",
        "MONGO_DB_NAME": "deadline10db",
        "RCS_HTTP_PORT_HOST": "8888",
        "RCS_HTTP_PORT_CONTAINER": "8888",
        "WEBSERVICE_HTTP_PORT_HOST": "8899",
        "WEBSERVICE_HTTP_PORT_CONTAINER": "8899",
        "MONGO_DB_PORT_HOST": "21017",
        "MONGO_DB_PORT_CONTAINER": "21017",
        "DEFAULT_DBPATH_CONTAINER": "/data/db",
        # "DEFAULT_DBPATH_CONTAINER": "/opt/Thinkbox/DeadlineDatabase10/mongo/data",
        "DEFAULT_CONFIG_DBPATH": "/data/configdb",
        "ROOT_DOMAIN": "farm.evil",
        # "DB_HOST": "mongodb-10-2",
        # https://vfxplatform.com/
        "PYTHON_MAJ": "3",
        "PYTHON_MIN": "11",
        "PYTHON_PAT": "11",
        # # PROD
        # "LN_NFS": "/nfs",
        # "NFS_ENTRY_POINT": "/data/share{0[LN_NFS]}",
        # "NFS_ENTRY_POINT_LNS": "{0[LN_NFS]}",
        # "INSTALLERS_ROOT": "{0[NFS_ENTRY_POINT]}/installers",
        # "NFS_REPOSITORY": "{0[NFS_ENTRY_POINT]}/prod/DeadlineRepository10",
        # "NFS_DEADLINE": "{0[NFS_ENTRY_POINT]}/prod/Deadline10",
        # "MONGO_DB_DIR_HOST": pathlib.Path("~/git/repos/studio-landscapes/tests/fixtures/10.2/DeadlineDatabase10/mongo/data").expanduser().as_posix(),
        # # TEST
        # "LN_NFS": "/nfs",
        # "NFS_ENTRY_POINT": "/data/share/nfs",
        # "NFS_ENTRY_POINT_LNS": "/nfs",
        # "INSTALLERS_ROOT": "/data/share/nfs/installers",
        # "MONGO_DB_DIR_HOST": pathlib.Path("~/git/repos/studio-landscapes/tests/fixtures/10.2/DeadlineDatabase10/mongo/data").expanduser().as_posix(),
        # "MONGO_DB_DIR_HOST": pathlib.Path("~/git/repos/studio-landscapes/tests/fixtures/v10_2/DeadlineDatabase10").expanduser().as_posix(),
        # # TODO
        # # DEADLINE_CLIENT_DIR: "/opt/Thinkbox/Deadline10"
        # # DEADLINE_REPO_DIR: "/opt/Thinkbox/DeadlineRepository10"
        # # MONGO_DB_NAME: deadline10db
        # # MONGO_DB_HOST: $DB_HOST
        # # MONGO_DB_PROD:
        # # MONGO_DB_TEST:
    }

    _env_mongo_express = {
        # "MONGO_PORT": "${MONGO_DB_PORT_CONTAINER}",
        # https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/#additional
        # -information-1
        # https://hub.docker.com/_/mongo-express/
        "ME_CONFIG_BASICAUTH_USERNAME": "web",
        "ME_CONFIG_BASICAUTH_PASSWORD": "web",
        "ME_CONFIG_OPTIONS_EDITORTHEME": "darcula",
        "ME_CONFIG_MONGODB_SERVER": "mongodb-10-2",
        "ME_CONFIG_MONGODB_PORT": "{MONGO_DB_PORT_CONTAINER}",
        # Todo:
        #  - [ ] Verify whether MONGO_DB_PORT_CONTAINER or MONGO_DB_PORT_HOST
        #        is actually correct
        "ME_CONFIG_MONGODB_URL": "mongodb://admin:pass@localhost:{MONGO_DB_PORT_CONTAINER}/db?ssl=false",
    }

    _env.update(_env_mongo_express)

    _env.update(secrets)
    _env.update(landscape_id)
    _env.update(nfs)
    # @formatter:on

    env_json = pathlib.Path(
        _env["DOT_LANDSCAPES"],
        _env.get("LANDSCAPE", "default"),
        "__".join(context.asset_key.path),
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

    yield Output(_env)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_env),
            "json": MetadataValue.path(env_json),
        },
    )


@asset(
    **asset_header,
    group_name="Build_Base_Image",
)
def pip_packages(
    context: AssetExecutionContext,
) -> Generator[Output[list] | AssetMaterialization | Any, Any, None]:
    """ """

    _pip_packages: list = [
        # Todo:
        #  - [ ] enable open-studio-landscapes after publish
        #  - [ ] maybe move dagster stuff to dagster image?
        # "open-studio-landscapes[dev] @ git+https://github.com/michimussato/open-studio-landscapes.git@main",
        "dagster-shared[dev] @ git+https://github.com/michimussato/dagster-shared.git@main",
        # "deadline-dagster[dev] @ git+https://github.com/michimussato/deadline-dagster.git@main",
        "docker-compose-graph[dev] @ git+https://github.com/michimussato/docker-compose-graph.git@main",
        "dagster-job-processor[dev] @ git+https://github.com/michimussato/dagster-job-processor.git@main",
    ]

    yield Output(_pip_packages)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_pip_packages),
        },
    )


@asset(
    **asset_header,
    group_name="Build_Base_Image",
)
def apt_packages(
    context: AssetExecutionContext,
) -> Generator[
    Output[dict[str, list[str | Any] | list[str]]] | AssetMaterialization | Any,
    Any,
    None,
]:
    """ """

    _apt_packages = dict()

    _apt_packages["base"] = [
        "git",
        "ca-certificates",
        "htop",
        "file",
        "tzdata",
        "curl",
        "wget",
        "ffmpeg",
        "xvfb",
        "libegl1",
        "libsm6",
        "libsm6",
        "libglu1-mesa",
        "libxss1",
    ]

    _apt_packages["build_python311"] = [
        "build-essential",
        "pkg-config",
        "zlib1g-dev",
        "libncurses5-dev",
        "libgdbm-dev",
        "libnss3-dev",
        "libssl-dev",
        "libreadline-dev",
        "libffi-dev",
        "libsqlite3-dev",
        "libbz2-dev",
    ]

    yield Output(_apt_packages)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_apt_packages),
        },
    )


@asset(
    **asset_header,
    group_name="Build_Base_Image",
    ins={
        "env": AssetIn(AssetKey([KEY, "env"])),
        "apt_packages": AssetIn(AssetKey([KEY, "apt_packages"])),
        "pip_packages": AssetIn(AssetKey([KEY, "pip_packages"])),
    },
)
def build_docker_image(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    apt_packages: dict[str, list[str]],  # pylint: disable=redefined-outer-name
    pip_packages: list,  # pylint: disable=redefined-outer-name
) -> Generator[Output[str] | AssetMaterialization | Any, Any, None]:
    """ """

    docker_file = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        "Dockerfiles",
        "__".join(context.asset_key.path),
        "Dockerfile",
    )

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    tags = [
        f"{env.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:latest",
        f"{env.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:{env.get('LANDSCAPE', str(time.time()))}",
    ]

    apt_install_str_base: str = get_apt_install_str(
        apt_install_packages=apt_packages["base"],
    )

    apt_install_str_build_python311: str = get_apt_install_str(
        apt_install_packages=apt_packages["build_python311"],
    )

    pip_install_str: str = get_pip_install_str(pip_install_packages=pip_packages)

    # @formatter:off
    docker_file_str = textwrap.dedent(
        """
        # {auto_generated}
        # {dagster_url}
        FROM ubuntu:20.04 AS {image_name}
        LABEL authors="{AUTHOR}"

        ARG DEBIAN_FRONTEND=noninteractive

        ENV CONTAINER_TIMEZONE={TIMEZONE}
        ENV SET_CONTAINER_TIMEZONE=true

        RUN apt-get update && apt-get upgrade -y

        {apt_install_str_base}

        {apt_install_str_build_python311}

        WORKDIR /build/python

        RUN curl "https://www.python.org/ftp/python/{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}/Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz" -o Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz
        RUN file Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz
        RUN tar -xvf Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz

        RUN cd Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT} && ./configure --enable-optimizations  # Todo: --prefix  # https://stackoverflow.com/questions/11307465/destdir-and-prefix-of-make
        RUN cd Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT} && make -j $(nproc)
        RUN cd Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT} && make altinstall  # altinstall instead of install because the later command will overwrite the default system python3 binary.

        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install pip --upgrade

        {pip_install_str}
        # RUN thinkbox-ssl-gen --help

        RUN rm -rf /build/python

        RUN apt-get clean

        ENTRYPOINT []
    """
    ).format(
        apt_install_str_base=apt_install_str_base,
        apt_install_str_build_python311=apt_install_str_build_python311,
        pip_install_str=pip_install_str.format(
            **env,
        ),
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(
            f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}",
            safe=":/%",
        ),
        image_name="__".join(context.asset_key.path).lower(),
        **env,
    )
    # @formatter:on

    with open(docker_file, "w") as fw:
        fw.write(docker_file_str)

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        cache=DOCKER_USE_CACHE,
        tags=tags,
        stream_logs=True,
    )

    log: str = ""

    for msg in stream:
        context.log.debug(msg)
        log += msg

    cmds_docker = compile_cmds(
        docker_file=docker_file,
        tag=tags[1],
        volumes=[],
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **asset_header,
    group_name="Environment",
)
def nfs(
    context: AssetExecutionContext,
) -> Generator[Output[dict] | AssetMaterialization | Any, Any, None]:
    # @formatter:off
    _env: dict = {
        "NFS_ENTRY_POINT": pathlib.Path("/data/share/nfs").as_posix(),
        "NFS_ENTRY_POINT_LNS": pathlib.Path("/nfs").as_posix(),
        "INSTALLERS_ROOT": pathlib.Path("/data/share/nfs/installers").as_posix(),
    }
    # @formatter:on

    yield Output(_env)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_env),
        },
    )


@asset(
    **asset_header,
    group_name=f"{KEY}_compose",
    ins={
        "ayon": AssetIn(
            AssetKey(["Ayon", "group_out"]),
        ),
    },
)
def compose_include(
    context: AssetExecutionContext,
    ayon: dict,  # pylint: disable=redefined-outer-name
) -> dict:

    compose_override_ayon = copy.deepcopy(ayon["docker_compose"])

    docker_dict = {
        "include": [
            compose_override_ayon,
        ],
    }

    # docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            # "docker_dict": MetadataValue.md(
            #     f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
            # ),
            # "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
        },
    )


# @asset(
#     **asset_header,
#     group_name=f"{KEY}_compose",
#     ins={
#         "env": AssetIn(
#             AssetKey([KEY, "env"]),
#         ),
#     },
# )
# def compose_networks(
#     context: AssetExecutionContext,
#     env: dict,  # pylint: disable=redefined-outer-name
# ) -> Generator[
#     Output[dict[str, dict[str, dict[str, str]]]] | AssetMaterialization | Any, Any, None
# ]:
#     docker_dict = {
#         "networks": {
#             "mongodb": {
#                 "name": "network_mongodb-10-2",
#             },
#             "repository": {
#                 "name": "network_repository-10-2",
#             },
#             "ayon": {
#                 "name": "network_ayon-10-2",
#             },
#         },
#     }
#
#     docker_yaml = yaml.dump(docker_dict)
#
#     yield Output(docker_dict)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
#             "docker_dict": MetadataValue.md(
#                 f"```json\n{json.dumps(docker_dict, indent=2)}\n```"
#             ),
#             "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
#             "env_10_2": MetadataValue.json(env),
#         },
#     )


@asset(
    **asset_header,
    group_name=f"{KEY}_compose",
    ins={
        "group_out": AssetIn(
            AssetKey([KEY, "group_out"]),
        ),
        # "compose_networks_10_2": AssetIn(
        #     AssetKey([KEY, "compose_networks"]),
        # ),
        # "compose_include_10_2": AssetIn(
        #     AssetKey([KEY, "compose_include"]),
        # ),
        "filebrowser": AssetIn(AssetKey(["filebrowser", "group_out"])),
        "grafana": AssetIn(AssetKey(["Grafana", "group_out"])),
        "dagster": AssetIn(AssetKey(["Dagster", "group_out"])),
        "likec4": AssetIn(AssetKey(["LikeC4", "group_out"])),
        "kitsu": AssetIn(AssetKey(["Kitsu", "group_out"])),
        "compose_include": AssetIn(AssetKey([KEY, "compose_include"])),
    },
)
def compose(
    context: AssetExecutionContext,
    group_out: dict,  # pylint: disable=redefined-outer-name
    # compose_networks_10_2: dict,  # pylint: disable=redefined-outer-name
    filebrowser: dict,  # pylint: disable=redefined-outer-name
    grafana: dict,  # pylint: disable=redefined-outer-name
    dagster: dict,  # pylint: disable=redefined-outer-name
    likec4: dict,  # pylint: disable=redefined-outer-name
    kitsu: dict,  # pylint: disable=redefined-outer-name
    compose_include: dict,  # pylint: disable=redefined-outer-name
) -> dict:
    """ """

    env = copy.deepcopy(group_out["env"])

    compose_filebrowser = copy.deepcopy(filebrowser["docker_compose"])
    compose_likec4 = copy.deepcopy(likec4["docker_compose"])
    compose_kitsu = copy.deepcopy(kitsu["docker_compose"])
    compose_grafana = copy.deepcopy(grafana["docker_compose"])
    compose_dagster = copy.deepcopy(dagster["docker_compose"])
    # compose_include = copy.deepcopy(dagster["docker_compose"])

    docker_chainmap = ChainMap(
        compose_kitsu,
        compose_likec4,
        compose_dagster,
        compose_grafana,
        compose_filebrowser,
        compose_include,
        # compose_networks_10_2,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)
    docker_yaml = yaml.dump(docker_dict)

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

    # project_name = f"{'__'.join(context.asset_key.path).lower()}__{env.get('LANDSCAPE', 'default').replace('.', '-')}"
    #
    # cmd_docker_compose_up = [
    #     shutil.which("docker"),
    #     "compose",
    #     "--file",
    #     docker_compose.as_posix(),
    #     "--project-name",
    #     project_name,
    #     "up",
    #     "--remove-orphans",
    # ]
    #
    # cmd_docker_compose_down = [
    #     shutil.which("docker"),
    #     "compose",
    #     "--file",
    #     docker_compose.as_posix(),
    #     "--project-name",
    #     project_name,
    #     "down",
    #     "--remove-orphans",
    # ]

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            # "cmd_docker_compose_up": MetadataValue.path(
            #     " ".join(shlex.quote(s) for s in cmd_docker_compose_up)
            # ),
            # "cmd_docker_compose_down": MetadataValue.path(
            #     " ".join(shlex.quote(s) for s in cmd_docker_compose_down)
            # ),
            # "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
            # "maps": MetadataValue.md(
            #     f"```json\n{json.dumps(docker_chainmap.maps, indent=2)}\n```"
            # ),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            # "env": MetadataValue.json(env),
        },
    )


@asset(
    **asset_header,
    group_name=KEY,
    ins={
        "env": AssetIn(AssetKey([KEY, "env"])),
        "build_docker_image": AssetIn(
            AssetKey([KEY, "build_docker_image"]),
        ),
    },
)
def group_out(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    build_docker_image: str,  # pylint: disable=redefined-outer-name
) -> dict[str, str | dict]:

    out_dict: dict = dict()

    out_dict["env"] = env
    out_dict["docker_image"] = build_docker_image

    yield Output(out_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(out_dict),
        },
    )
