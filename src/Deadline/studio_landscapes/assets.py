import uuid
from datetime import datetime
import json
import shutil
import textwrap
import pathlib
import time

from Deadline.studio_landscapes.constants import *
from Deadline.studio_landscapes.utils import *

from python_on_whales import docker

from dagster import (
    AssetExecutionContext,
    asset,
    Output,
    AssetMaterialization,
    MetadataValue,
    AssetIn,
)


@asset(
    group_name="Environment",
    compute_kind="python",
)
def git_root(
        context: AssetExecutionContext,
) -> pathlib.Path:

    _git_root = get_git_root()

    yield Output(_git_root)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[-1]: MetadataValue.path(_git_root),

        },
    )


@asset(
    group_name="Environment",
    compute_kind="python",
)
def landscape_id(
        context: AssetExecutionContext,
) -> dict:

    now = datetime.now()

    landscape_stamp = {
        "LANDSCAPE": f"{datetime.strftime(now, '%Y-%m-%d_%H-%M-%S')}__{uuid.uuid4().hex}",
    }

    yield Output(landscape_stamp)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[-1]: MetadataValue.json(landscape_stamp),

        },
    )


@asset(
    group_name="Environment",
    compute_kind="python",
)
def secrets(
        context: AssetExecutionContext,
) -> dict:
    try:
        from __SECRET__.secrets import secrets as _secrets
    except ModuleNotFoundError:
        context.log.exception("Failed to import secrets from __SECRET__.secrets")
        _secrets: dict = {}

    yield Output(_secrets)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[-1]: MetadataValue.json(_secrets),

        },
    )


@asset(
    group_name="Environment",
    compute_kind="python",
    ins={
        "git_root": AssetIn(),
        "secrets": AssetIn(),
        "landscape_id": AssetIn(),
        "nfs": AssetIn(),
    },
)
def env_base(
        context: AssetExecutionContext,
        git_root: pathlib.Path,
        secrets: dict,
        landscape_id: dict,
        nfs: dict,
) -> dict:
    # @formatter:off

    dot_docker = git_root / ".docker"
    dot_docker.mkdir(
        parents=True,
        exist_ok=True,
    )

    _env: dict = {

        "GIT_ROOT": git_root.as_posix(),
        "DOT_DOCKER": dot_docker.as_posix(),

        "AUTHOR": "michimussato@gmail.com",
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
        # "MONGO_DB_DIR_HOST": pathlib.Path("~/git/repos/studio-landscapes/tests/fixtures/10_2/DeadlineDatabase10").expanduser().as_posix(),

        # # TODO
        # # DEADLINE_CLIENT_DIR: "/opt/Thinkbox/Deadline10"
        # # DEADLINE_REPO_DIR: "/opt/Thinkbox/DeadlineRepository10"
        # # MONGO_DB_NAME: deadline10db
        # # MONGO_DB_HOST: $DB_HOST
        # # MONGO_DB_PROD:
        # # MONGO_DB_TEST:
    }

    _env_ayon = {
        "AYON_DOCKER_COMPOSE": pathlib.Path(
            _env["GIT_ROOT"],
            "repos",
            "ayon-docker",
            "docker-compose.yml",
        ).expanduser().as_posix(),
        "AYON_PORT_HOST": "5005",
        "AYON_PORT_CONTAINER": "5000",
    }

    _env_dagster = {
        "DAGSTER_DEV_PORT_HOST": "3003",
        "DAGSTER_DEV_PORT_CONTAINER": "3006",
        "DAGSTER_ROOT": "/dagster",
        "DAGSTER_HOME": "/dagster/materializations",
        "DAGSTER_HOST": "0.0.0.0",
        "DAGSTER_WORKSPACE": "/dagster/workspace.yaml",
    }

    _env_filebrowser = {
        "FILEBROWSER_PORT_HOST": "8080",
        "FILEBROWSER_PORT_CONTAINER": "80",
        "FILEBROWSER_DB": pathlib.Path(
            _env["GIT_ROOT"],
            "configs",
            "filebrowser",
            "db",
            "filebrowser.db",
        ).expanduser().as_posix(),
        "FILEBROWSER_JSON": pathlib.Path(
            _env["GIT_ROOT"],
            "configs",
            "filebrowser",
            "json",
            "filebrowser.json",
        ).expanduser().as_posix(),
    }

    _env_likec4 = {
        "LIKEC4_DEV_PORT_HOST": "4567",
        "LIKEC4_DEV_PORT_CONTAINER": "4567",
        "LIKEC4_HOST": "0.0.0.0",
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

    _env_kitsu = {
        "KITSU_ADMIN_USER": "admin@example.com",
        "KITSU_ADMIN_PASSWORD": "mysecretpassword",
        "KITSU_PORT_HOST": "4545",
        "KITSU_PORT_CONTAINER": "80",
        "KITSU_DATABASE_INSTALL_DESTINATION": {
            #################################################################
            # Kitsu Postgresql DB will be created in (hardcoded):
            # "KITSU_DATABASE_INSTALL_DESTINATION" / "postgresql" / "14" / "main"
            # Kitsu Previews folder will be created in (hardcoded):
            # "KITSU_DATABASE_INSTALL_DESTINATION" / "previews"
            #################################################################
            #################################################################
            # Inside Landscape:
            "default": pathlib.Path(
                _env["DOT_DOCKER"],
                "landscapes",
                landscape_id.get("LANDSCAPE", "default"),
                "data",
                "kitsu",
            ).as_posix(),
            #################################################################
            # Prod DB:
            "prod_db": pathlib.Path(
                nfs["NFS_ENTRY_POINT"],
                "services",
                "kitsu",
            ).as_posix(),
            #################################################################
            # Test DB:
            "test_db": pathlib.Path(
                nfs["NFS_ENTRY_POINT"],
                "test_data",
                "10.2",
                "kitsu",
            ).as_posix(),
        }["default"],
        f"KITSU_INIT_ZOU": pathlib.Path(
            _env["DOT_DOCKER"],
            "landscapes",
            landscape_id.get("LANDSCAPE", "default"),
            "configs",
            "kitsu",
            "init_zou.sh",
        ).expanduser().as_posix(),
        f"KITSU_TEMPLATE_DB_14": pathlib.Path(
            _env["GIT_ROOT"],
            "configs",
            "kitsu",
            "postgres",
            "template_dbs",
            "14",
            "main"
        ).expanduser().as_posix(),
    }

    _env.update(_env_ayon)
    _env.update(_env_dagster)
    _env.update(_env_kitsu)
    _env.update(_env_filebrowser)
    _env.update(_env_likec4)
    _env.update(_env_mongo_express)

    _env.update(secrets)
    _env.update(landscape_id)
    _env.update(nfs)
    # @formatter:on

    env_json = pathlib.Path(
        _env["DOT_DOCKER"],
        "landscapes",
        _env.get("LANDSCAPE", "default"),
        f"{context.asset_key.path[-1]}.json",
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
            context.asset_key.path[-1]: MetadataValue.json(_env),
            "json": MetadataValue.path(env_json),
        },
    )


@asset(
    group_name="Build_Base_Image",
    compute_kind="python",
)
def pip_packages_base_image(
        context: AssetExecutionContext,
) -> list:
    """
    """

    pip_packages: list = [
        "dagster-shared[dev] @ git+https://github.com/michimussato/dagster-shared.git@main",
        "deadline-dagster[dev] @ git+https://github.com/michimussato/deadline-dagster.git@main",
    ]

    yield Output(pip_packages)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[-1]: MetadataValue.json(pip_packages),
        },
    )


@asset(
    group_name="Build_Base_Image",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
        "pip_packages_base_image": AssetIn(),
    },
)
def build_base_image(
        context: AssetExecutionContext,
        env_base: dict,
        pip_packages_base_image: list,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        env_base["DOT_DOCKER"],
        "landscapes",
        env_base.get("LANDSCAPE", "default"),
        "Dockerfiles",
        context.asset_key.path[0],
        "Dockerfile",
    )
    tags = [
        f"{env_base.get('IMAGE_PREFIX')}/{context.asset_key.path[-1]}:latest",
        f"{env_base.get('IMAGE_PREFIX')}/{context.asset_key.path[-1]}:{env_base.get('LANDSCAPE', str(time.time()))}",
    ]

    pip_install_str: str = get_pip_install_str(
        pip_install_packages=pip_packages_base_image
    )

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # {auto_generated}
        FROM ubuntu:20.04 AS {image_name}
        LABEL authors="{AUTHOR}"
        
        ARG DEBIAN_FRONTEND=noninteractive
        
        ENV CONTAINER_TIMEZONE="Europe/Zurich"
        ENV SET_CONTAINER_TIMEZONE=true
        
        RUN apt-get update \
            && apt-get upgrade -y
        
        RUN apt-get install \
            -y \
            --no-install-recommends \
            git \
            ca-certificates \
            htop  \
            file  \
            tzdata  \
            curl  \
            wget  \
            ffmpeg  \
            xvfb  \
            libegl1  \
            libsm6  \
            libsm6  \
            libglu1-mesa  \
            libxss1
        
        RUN apt-get install  \
            -y  \
            --no-install-recommends  \
            make  \
            build-essential  \
            zlib1g-dev  \
            libncurses5-dev  \
            libgdbm-dev  \
            libnss3-dev  \
            libssl-dev  \
            libreadline-dev  \
            libffi-dev  \
            libsqlite3-dev  \
            libbz2-dev
        
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
    """).format(
        pip_install_str=pip_install_str.format(
            **env_base,
        ),
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[-1]}",
        image_name=context.asset_key.path[-1],
        **env_base,
    )
    # @formatter:on

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

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
            context.asset_key.path[-1]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Environment",
    compute_kind="python",
)
def nfs(
        context: AssetExecutionContext,
) -> dict[str, str]:
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
            context.asset_key.path[-1]: MetadataValue.json(_env),
        },
    )


# @asset(
#     group_name="Environment",
#     compute_kind="python",
#     ins={
#         "nfs": AssetIn(),
#     },
# )
# def repository_dirs(
#         context: AssetExecutionContext,
#         nfs: dict,
# ) -> dict:
#     # @formatter:off
#     _env: dict = {
#         "DEADLINE_REPO_DICTS": {
#             "10_2": {
#                 "INSTALLER": None,
#                 "PROD": {
#                     "INSTALL_DEST_REPOSITORY": pathlib.PurePath(
#                         nfs.get("NFS_ENTRY_POINT"),
#                         "deadline_repository_10_prod",
#                         "DeadlineRepository10"
#                     ).as_posix(),
#                 },
#                 # "TEST": {
#                 #     "INSTALL_DEST_REPOSITORY": pathlib.PurePath(
#                 #         nfs.get("NFS_ENTRY_POINT"),
#                 #         "deadline_repository_10_test",
#                 #         "DeadlineRepository10"
#                 #     ).as_posix(),
#                 # },
#                 "TEST": {
#                     "INSTALL_DEST_REPOSITORY": pathlib.PurePath(
#                         nfs.get("NFS_ENTRY_POINT"),
#                         "test_data",
#                         "opt",
#                         "Thinkbox",
#                         "DeadlineRepository10",
#                     ).as_posix(),
#                 },
#             },
#         },
#     }
#     # @formatter:on
#
#     _env.update(nfs)
#
#     yield Output(_env)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             context.asset_key.path[0]: MetadataValue.json(_env),
#
#         },
#     )
