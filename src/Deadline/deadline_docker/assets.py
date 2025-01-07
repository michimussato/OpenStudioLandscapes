import json
import shutil
import textwrap
import pathlib
import time
import yaml
from collections import ChainMap
from functools import reduce

from python_on_whales import docker

from dagster import (
    AssetExecutionContext,
    asset,
    Output,
    AssetMaterialization,
    MetadataValue,
    AssetIn,
)

USE_CACHE = False


def deep_merge(dict1, dict2):
    """https://sqlpey.com/python/solved-top-5-methods-to-deep-merge-dictionaries-in-python/"""
    for key in dict2:
        if key in dict1 and isinstance(dict1[key], dict) and isinstance(dict2[key], dict):
            deep_merge(dict1[key], dict2[key])
        else:
            dict1[key] = dict2[key]
    return dict1


def compile_cmds(
        docker_file,
        tag,
) -> dict[str, MetadataValue]:
    cmd_docker_run = f"docker run --rm -it --entrypoint bash {tag}"
    cmd_docker_build = (
        f"docker build --tag {tag} {docker_file.parent.as_posix()} {'--no-cache' if USE_CACHE else ''}"
    )

    metadata_values = {
        "cmd_docker_run": MetadataValue.path(cmd_docker_run),
        "cmd_docker_build": MetadataValue.path(cmd_docker_build),
    }

    return metadata_values


@asset(
    group_name="Maintenance",
    compute_kind="python",
)
def docker_cleanup(
        context: AssetExecutionContext,
):
    out = {
        "stdout": context.log.info,
        "stderr": context.log.error,
    }

    containers = docker.container.list(
        all=True
    )

    docker.container.stop(
        containers=containers,
    )

    stream_container_prune = docker.container.prune(
        stream_logs=True,
    )

    # log_container_prune_stdout: str = ""
    # log_container_prune_stderr: str = ""

    # for msg in stream_container_prune:
    #     out[msg[0]](msg)
    #     # context.log.debug(msg)
    #     # locals(f"")
    #     # log_container_prune += msg

    docker.image.prune(
        all=True,
    )

    docker.volume.prune(
        all=True,
    )

    stream_buildx_prune = docker.buildx.prune(
        all=True,
        stream_logs=True,
    )

    # log_buildx_prune: str = ""

    # for msg in stream_buildx_prune:
    #     out[msg[0]](msg)

    docker.network.prune()

    return None


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
            context.asset_key.path[0]: MetadataValue.json(_secrets),

        },
    )


@asset(
    group_name="Environment",
    compute_kind="python",
    ins={
        "secrets": AssetIn(),
    },
)
def env_base(
        context: AssetExecutionContext,
        secrets: dict,
) -> dict:
    # @formatter:off
    _env: dict = {
        "AUTHOR": "michimussato@gmail.com",
        "MONGO_EXPRESS_PORT_HOST": "8181",
        "MONGO_EXPRESS_PORT_CONTAINER": "8081",

        "MONGO_DB_NAME": "deadline10db",
        "MONGO_DB_HOST": "mongodb-10-2",

        "LIKEC4_DEV_PORT_HOST": "4567",
        "LIKEC4_DEV_PORT_CONTAINER": "4567",
        "LIKEC4_HOST": "0.0.0.0",

        "FILEBROWSER_PORT_HOST": "8080",
        "FILEBROWSER_PORT_CONTAINER": "80",

        "DAGSTER_DEV_PORT_HOST": "3003",
        "DAGSTER_DEV_PORT_CONTAINER": "3006",
        "DAGSTER_DAGSTER_WORKSPACE": "/dagster",
        "DAGSTER_HOME": "/dagster/materializations",
        "DAGSTER_HOST": "0.0.0.0",
        "DAGSTER_WORKSPACE": "/dagster/workspace.yaml",

        "RCS_HTTP_PORT_HOST": "8888",
        "RCS_HTTP_PORT_CONTAINER": "8888",

        # "WEBSERVICE_HTTP_PORT_HOST": 8899,
        "WEBSERVICE_HTTP_PORT_CONTAINER": "8899",

        "MONGO_DB_PORT_HOST": "21017",
        "MONGO_DB_PORT_CONTAINER": "21017",
        # "MONGO_PORT": "${MONGO_DB_PORT_CONTAINER}",
        # https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/#additional
        # -information-1
        # https://hub.docker.com/_/mongo-express/
        "ME_CONFIG_BASICAUTH_USERNAME": "web",
        "ME_CONFIG_BASICAUTH_PASSWORD": "web",
        "ME_CONFIG_OPTIONS_EDITORTHEME": "darcula",
        "ME_CONFIG_MONGODB_SERVER": "mongodb-10-2",
        "ME_CONFIG_MONGODB_PORT": "{MONGO_DB_PORT_CONTAINER}",
        "ME_CONFIG_MONGODB_URL": "mongodb://admin:pass@localhost:{MONGO_DB_PORT_CONTAINER}/db?ssl=false",

        # "AYON_PORT_HOST": 5005,
        # "AYON_PORT_CONTAINER": 5000,
        #
        # "KITSU_PORT_HOST": 8181,
        # "KITSU_PORT_CONTAINER": 80,
        # #"SECRETS_USERNAME": "SecretsAdmin",
        # #"SECRETS_PASSWORD": "%ecretsPassw0rd!",
        "ROOT_DOMAIN": "farm.evil",
        # "DB_HOST": "mongodb-10-2",

        # "PYTHON_VERSION": "3.11.11",
        "PYTHON_MAJ": "3",
        "PYTHON_MIN": "11",
        "PYTHON_PAT": "11",

        "NFS_ENTRY_POINT": "/data/share/nfs",
        "TEST_NFS_ENTRY_POINT": "/data/share/nfs",
        "NFS_ENTRY_POINT_LNS": "/nfs",
        "TEST_NFS_ENTRY_POINT_LNS": "/nfs",
        "INSTALLERS_ROOT": "/data/share/nfs/installers",
        "TEST_INSTALLERS_ROOT": "/data/share/nfs/installers",

        # # TODO
        # # DEADLINE_INI:
        # # DEADLINE_CLIENT_DIR: "/opt/Thinkbox/Deadline10"
        # # DEADLINE_REPO_DIR: "/opt/Thinkbox/DeadlineRepository10"
        # # MONGO_DB_NAME: deadline10db
        # # MONGO_DB_HOST: $DB_HOST
        # # MONGO_DB_PROD:
        # # MONGO_DB_TEST:
    }

    _env.update(secrets)
    # @formatter:on

    yield Output(_env)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(_env),

        },
    )


@asset(
    group_name="Environment_10_2",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
    },
)
def env_10_2(
        context: AssetExecutionContext,
        env_base: dict,
) -> dict:
    # @formatter:off
    _env: dict = {
        "DEADLINE_VERSION": "10.2.1.1",

        "GOOGLE_ID_AWSPortalLink_10_2": "1VOQa6OyYUZj_7VILcD6EVl7YOfYVlCrU",
        "GOOGLE_ID_DeadlineClient_10_2": "1cGxCPkrJ1ujWqie2yXTrOpShkEgSXR0F",
        "GOOGLE_ID_DeadlineRepository_10_2": "1VZhCcxvCAc4oozLAKRCv_zwQLMuVdMRz",
    }
    # @formatter:on

    env_base.update(_env)

    yield Output(env_base)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(env_base),
            "update": MetadataValue.json(_env),
        },
    )


@asset(
    group_name="Build_Base_Image",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
    },
)
def build_base_image(
        context: AssetExecutionContext,
        env_base: dict,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        f"~/git/repos/deadline-docker/10.2/.docker/Dockerfiles/{context.asset_key.path[0]}/Dockerfile"
    ).expanduser()
    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # AUTO-GENERATED
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
        
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore "deadline-dagster @ git+https://github.com/michimussato/deadline-dagster.git@main"
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared @ git+https://github.com/michimussato/dagster-shared.git@main"
        # RUN thinkbox-ssl-gen --help
        
        RUN rm -rf /build/python
        
        RUN apt-get clean
        
        ENTRYPOINT []
    """).format(
        image_name=context.asset_key.path[0],
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
        cache=USE_CACHE,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Build_Images_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_base_image": AssetIn(),
    },
)
def build_base_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_base_image: str,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        f"~/git/repos/deadline-docker/10.2/.docker/Dockerfiles/{context.asset_key.path[0]}/Dockerfile"
    ).expanduser()

    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # AUTO-GENERATED
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        SHELL ["/bin/bash", "-c"]
        
        RUN apt-get update \
            && apt-get upgrade -y
        
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore git+https://github.com/michimussato/SSLGeneration.git@packaging
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore git+https://github.com/michimussato/DeadlineWrapper.git@main
        
        WORKDIR /installers
        
        RUN wget -O AWSPortalLink.run "https://www.googleapis.com/drive/v3/files/{GOOGLE_ID_AWSPortalLink_10_2}?alt=media&key={GOOGLE_API_KEY}"
        RUN chmod a+x AWSPortalLink.run
        RUN wget -O DeadlineClient.run "https://www.googleapis.com/drive/v3/files/{GOOGLE_ID_DeadlineClient_10_2}?alt=media&key={GOOGLE_API_KEY}"
        RUN chmod a+x DeadlineClient.run
        RUN wget -O DeadlineRepository.run "https://www.googleapis.com/drive/v3/files/{GOOGLE_ID_DeadlineRepository_10_2}?alt=media&key={GOOGLE_API_KEY}"
        RUN chmod a+x DeadlineRepository.run
        
        # RUN thinkbox-ssl-gen --help
        
        RUN apt-get clean
        
        ENTRYPOINT []
    """).format(
        image_name=context.asset_key.path[0],
        parent_image=build_base_image,
        **env_10_2,
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
        cache=USE_CACHE,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Build_Images_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_base_image_10_2": AssetIn(),
    },
)
def build_repository_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_base_image_10_2: str,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        "~/git/repos/deadline-docker/10.2/base_images/base_image/base_image_10_2/repo_installer/Dockerfile",
    ).expanduser()
    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # AUTO-GENERATED
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        SHELL ["/bin/bash", "-c"]
        
        WORKDIR /installers
        
        RUN deadline-wrapper-10-2  \
            -vv  \
            install-repository  \
            --installer /installers/DeadlineRepository.run  \
            --deadline-version {DEADLINE_VERSION}  \
            --prefix "/opt/Thinkbox/DeadlineRepository10"  \
            --dbtype "MongoDB"  \
            --dbhost {MONGO_DB_HOST}  \
            --dbport {MONGO_DB_PORT_HOST}  \
            --dbname {MONGO_DB_NAME}
        
        WORKDIR /opt/Thinkbox
        
        ENTRYPOINT []
    """).format(
        image_name=context.asset_key.path[0],
        parent_image=build_base_image_10_2,
        **env_10_2,
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
        cache=USE_CACHE,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


# @asset(
#     group_name="Build_Images_10_2",
#     ins={
#         "env_10_2": AssetIn(),
#         "build_repository_image_10_2": AssetIn(),
#     },
#     # deps=[
#     #     "build_base_image_10_2"
#     # ],
# )
# def build_rcs_image_10_2(
#         context: AssetExecutionContext,
#         build_repository_image_10_2: dict,
# ) -> str:
#     """
#     """
#
#     docker_file = pathlib.Path(
#         "/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/base_image_10_2/repo_installer/Dockerfile")
#     tags = [
#         "michimussato/repository_image_10_2:latest",
#         f"michimussato/repository_image_10_2:{str(time.time())}",
#     ]
#     buildargs = {
#         "DEADLINE_VERSION": env_10_2.get("DEADLINE_VERSION"),
#         "MONGO_DB_PORT_HOST": env_10_2.get("MONGO_DB_PORT_HOST"),
#         "MONGO_DB_NAME": env_10_2.get("MONGO_DB_NAME"),
#         "MONGO_DB_HOST": env_10_2.get("MONGO_DB_HOST"),
#     }
#
#     with open(docker_file, "r") as fr:
#         docker_file_content = fr.read()
#
#     context.log.info(f"{buildargs = }")
#
#     stream = docker.build(
#         context_path=docker_file.parent.as_posix(),
#         build_args=buildargs,
#         cache=USE_CACHE,
#         tags=tags,
#         stream_logs=True,
#     )
#
#     log: str = ""
#
#     for msg in stream:
#         context.log.debug(msg)
#         log += msg
#
#     cmds_docker = compile_cmds(
#         docker_file=docker_file,
#         tag=tags[1],
#         buildargs=buildargs,
#     )
#
#     yield Output(tags[1])
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             context.asset_key.path[0]: MetadataValue.path(tags[1]),
#             "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
#             **cmds_docker,
#             "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
#             "env_10_2": MetadataValue.json(env_10_2),
#         },
#     )


@asset(
    group_name="Build_Images_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_base_image_10_2": AssetIn(),
    },
)
def build_client_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_base_image_10_2: str,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        f"~/git/repos/deadline-docker/10.2/.docker/Dockerfiles/{context.asset_key.path[0]}/Dockerfile"
    ).expanduser()

    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # AUTO-GENERATED
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        SHELL ["/bin/bash", "-c"]
        
        WORKDIR /installers
        
        RUN deadline-wrapper-10-2  \
            -vv  \
            install-client  \
            --installer /installers/DeadlineClient.run  \
            --deadline-version {DEADLINE_VERSION}  \
            --prefix "/opt/Thinkbox/Deadline10"  \
            --repositorydir "/opt/Thinkbox/DeadlineRepository10"  \
            --httpport {RCS_HTTP_PORT_CONTAINER}  \
            --webservice-httpport {WEBSERVICE_HTTP_PORT_CONTAINER}
        
        WORKDIR /opt/Thinkbox
        
        ENTRYPOINT []
    """).format(
        image_name=context.asset_key.path[0],
        parent_image=build_base_image_10_2,
        **env_10_2,
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
        cache=USE_CACHE,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Build_Images_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_client_image_10_2": AssetIn(),
    },
)
def build_generic_runner_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_client_image_10_2: str,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        f"~/git/repos/deadline-docker/10.2/.docker/Dockerfiles/{context.asset_key.path[0]}/Dockerfile"
    ).expanduser()

    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # AUTO-GENERATED
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        SHELL ["/bin/bash", "-c"]
        
        ENTRYPOINT ["deadline-wrapper-10-2", "-vv", "run"]
        
        CMD ["--help"]
    """).format(
        image_name=context.asset_key.path[0],
        parent_image=build_client_image_10_2,
        **env_10_2,
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
        cache=USE_CACHE,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Common_Service_Images",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
        "build_base_image": AssetIn(),
    },
)
def build_dagster_dev(
        context: AssetExecutionContext,
        env_base: dict,
        build_base_image: str,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        f"~/git/repos/deadline-docker/10.2/.docker/Dockerfiles/{context.asset_key.path[0]}/Dockerfile"
    ).expanduser()

    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # AUTO-GENERATED
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"
        
        WORKDIR {DAGSTER_WORKSPACE}
        COPY ./payload/workspace.yaml .
        
        WORKDIR {DAGSTER_HOME}
        COPY ./payload/dagster.yaml .
        
        WORKDIR {DAGSTER_WORKSPACE}
        
        ENTRYPOINT ["dagster", "dev"]
        CMD []
    """).format(
        image_name=context.asset_key.path[0],
        parent_image=build_base_image,
        **env_base,
    )
    # @formatter:on

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_file, "w") as fw:
        fw.write(docker_file_str)

    payload = docker_file.parent / "payload"
    payload.mkdir(parents=True, exist_ok=True)

    # workspace.yaml
    shutil.copy(
        src=pathlib.Path("~/git/repos/deadline-docker/10.2/base_images/base_image/dagster_dev/config/workspace.yaml").expanduser(),
        dst=payload,
    )

    # dagster.yaml
    shutil.copy(
        src=pathlib.Path("~/git/repos/deadline-docker/10.2/base_images/base_image/dagster_dev/config/materializations/dagster.yaml").expanduser(),
        dst=payload,
    )

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        cache=USE_CACHE,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Common_Service_Images",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
        "build_base_image": AssetIn(),
    },
)
def build_likec4_dev(
        context: AssetExecutionContext,
        env_base: dict,
        build_base_image: str,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        f"~/git/repos/deadline-docker/10.2/.docker/Dockerfiles/{context.asset_key.path[0]}/Dockerfile"
    ).expanduser()

    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # AUTO-GENERATED
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        RUN apt-get update \
            && apt-get upgrade -y
        
        RUN apt-get install \
            -y \
            --no-install-recommends \
            unzip  \
            gpg  \
            gpg-agent
        
        WORKDIR /ENTRYPOINT
        
        COPY ./payload/setup.sh .
        COPY ./payload/run.sh .
        
        RUN chmod -R +x /ENTRYPOINT/*.sh
        
        RUN /usr/bin/env bash /ENTRYPOINT/setup.sh
        
        # https://stackoverflow.com/a/40454758/2207196
        ENTRYPOINT ["/usr/bin/env", "bash", "/ENTRYPOINT/run.sh", "yarn", "dev"]
        CMD []
    """).format(
        image_name=context.asset_key.path[0],
        parent_image=build_base_image,
        **env_base,
    )
    # @formatter:on

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_file, "w") as fw:
        fw.write(docker_file_str)

    payload = docker_file.parent / "payload"
    payload.mkdir(parents=True, exist_ok=True)

    # setup.sh
    shutil.copy(
        src=pathlib.Path("~/git/repos/deadline-docker/10.2/base_images/base_image/likec4_dev/entrypoint/setup.sh").expanduser(),
        dst=payload,
    )

    # run.sh
    shutil.copy(
        src=pathlib.Path("~/git/repos/deadline-docker/10.2/base_images/base_image/likec4_dev/entrypoint/run.sh").expanduser(),
        dst=payload,
    )

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        cache=USE_CACHE,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_base": MetadataValue.json(env_base),
        },
    )


# @asset(
#     group_name="Build_Images_10_2",
#     ins={
#         "env_10_2": AssetIn(),
#     },
#     deps=[
#         "build_client_image_10_2"
#     ],
# )
# def build_generic_runner_10_2(
#         context: AssetExecutionContext,
#         env_10_2: dict,
# ):
#     """
#     docker run --rm -it --entrypoint bash michimussato/generic_runner:latest
#     """
#
#     docker_file = pathlib.Path(
#         "/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/base_image_10_2/client_installer"
#         "/generic_runner/Dockerfile")
#     tag = "michimussato/generic_runner:latest"
#     buildargs = {}
#
#     with open(docker_file, "r") as fr:
#         context.log.info(fr.read())
#
#     base_image, build_logs = docker_build(
#         docker_file=docker_file,
#         tag=tag,
#         buildargs=buildargs,
#         nocache=True,
#     )
#
#     cmds_docker = compile_cmds(
#         docker_file=docker_file,
#         tag=tag,
#         buildargs=buildargs,
#     )
#
#     yield Output(base_image.id)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "docker_file": MetadataValue.json(base_image.id),
#             **cmds_docker,
#             "build_logs": MetadataValue.md(f"```shell\n{get_log(build_logs)}\n```"),
#             "env_10_2": MetadataValue.json(env_10_2),
#         },
#     )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
    },
)
def compose_networks_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> dict:
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

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
    },
)
def compose_mongo_express_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> dict:
    docker_dict = {
        "services": {
            "mongo-express-10-2": {
                "image": "mongo-express",
                "hostname": "mongo-express-10-2",
                "container_name": "mongo-express-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                "environment": {
                    "ME_CONFIG_BASICAUTH_USERNAME": env_10_2.get("ME_CONFIG_BASICAUTH_USERNAME"),
                    "ME_CONFIG_BASICAUTH_PASSWORD": env_10_2.get("ME_CONFIG_BASICAUTH_PASSWORD"),
                    "ME_CONFIG_OPTIONS_EDITORTHEME": env_10_2.get("ME_CONFIG_OPTIONS_EDITORTHEME"),
                    "ME_CONFIG_MONGODB_SERVER": env_10_2.get("ME_CONFIG_MONGODB_SERVER"),
                    "ME_CONFIG_MONGODB_PORT": str(env_10_2.get("ME_CONFIG_MONGODB_PORT")).format(
                        MONGO_DB_PORT_CONTAINER=env_10_2.get("MONGO_DB_PORT_CONTAINER")
                    ),
                    # "ME_CONFIG_MONGODB_URL": env_base.get(f"MONGO_DB_PORT_CONTAINER"),
                    "ME_CONFIG_MONGODB_URL": str(env_10_2.get("ME_CONFIG_MONGODB_URL")).format(
                        MONGO_DB_PORT_CONTAINER=env_10_2.get("MONGO_DB_PORT_CONTAINER")
                    ),
                },
                "depends_on": [
                    "mongodb-10-2",
                ],
                "networks": [
                    "mongodb",
                ],
                "ports": [
                    f"{env_10_2.get('MONGO_EXPRESS_PORT_HOST')}:{env_10_2.get('MONGO_EXPRESS_PORT_CONTAINER')}",
                ],
                # "volumes": [
                #     f"{env_base.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL:/opt/Thinkbox/DeadlineDatabase10/mongo/data",
                #     f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}:ro",
                #     f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}:ro",
                # ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
    },
)
def compose_filebrowser_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> dict:
    docker_dict = {
        "services": {
            "filebrowser": {
                "image": "filebrowser/filebrowser",
                "container_name": "filebrowser-10-2",
                "hostname": "filebrowser-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                # "depends_on": [
                #     "mongodb-10-2",
                # ],
                "networks": [
                    "repository",
                ],
                "ports": [
                    f"{env_10_2.get('FILEBROWSER_PORT_HOST')}:{env_10_2.get('FILEBROWSER_PORT_CONTAINER')}",
                ],
                "volumes": [
                    "/home/michael/git/repos/deadline-docker/10.2/databases/filebrowser/filebrowser.db:/filebrowser.db",
                    "/home/michael/git/repos/deadline-docker/10.2/configs/filebrowser/filebrowser.json:/.filebrowser.json",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL:/opt/Thinkbox/DeadlineDatabase10/mongo/data:ro",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}:ro",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}:ro",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
    },
)
def compose_mongodb_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> dict:
    docker_dict = {
        "services": {
            "mongodb-10-2": {
                "image": "mongodb/mongodb-community-server:4.4-ubuntu2004",
                "container_name": "mongodb-10-2",
                "hostname": "mongodb-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                # "depends_on": [],
                "command": [
                    "--port", env_10_2.get("MONGO_DB_PORT_CONTAINER"),
                    "--dbpath", "/opt/Thinkbox/DeadlineDatabase10/mongo/data",
                    "--bind_ip_all",
                    "--noauth",
                    "--storageEngine", "wiredTiger",
                    "--tlsMode", "disabled",
                ],
                "networks": [
                    "mongodb",
                    "repository",
                ],
                "ports": [
                    f"{env_10_2.get('MONGO_DB_PORT_HOST')}:{env_10_2.get('MONGO_DB_PORT_CONTAINER')}",
                ],
                "volumes": [
                    f"{env_10_2.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL:/opt/Thinkbox/DeadlineDatabase10/mongo/data",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}:ro",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}:ro",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
        "build_dagster_dev": AssetIn(),
    },
)
def compose_dagster_dev(
        context: AssetExecutionContext,
        env_base: dict,
        build_dagster_dev: str,
) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "dagster_dev": {
                "container_name": "dagster-dev-10-2",
                "hostname": "dagster-dev-10-2",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_dagster_dev,
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "environment": {
                    "DAGSTER_HOME": env_base.get('DAGSTER_HOME'),
                },
                "command": [
                    "--workspace",
                    env_base.get('DAGSTER_WORKSPACE'),
                    "--host",
                    env_base.get('DAGSTER_HOST'),
                    "--port",
                    env_base.get('DAGSTER_DEV_PORT_CONTAINER'),
                ],
                "volumes": [
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}",
                ],
                "ports": [
                    f"{env_base.get('DAGSTER_DEV_PORT_HOST')}:{env_base.get('DAGSTER_DEV_PORT_CONTAINER')}",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_repository_image_10_2": AssetIn(),
    },
)
def compose_repository_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_repository_image_10_2: str,
) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "repository_10_2": {
                "container_name": "repository-10-2",
                "hostname": "repository-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_repository_image_10_2,
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": [
                    "tail",
                    "-F",
                    "anything",
                ],
                "volumes": [
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
                    # Redirect to host installation for now:
                    f"/data/share/nfs/test_data/10.2/opt/Thinkbox/DeadlineRepository10:/opt/Thinkbox/DeadlineRepository10",
                ],
                # "ports": [
                #     f"{env_base.get('LIKEC4_DEV_PORT_HOST')}:{env_base.get('LIKEC4_DEV_PORT_CONTAINER')}",
                # ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            # "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
        "build_likec4_dev": AssetIn(),
    },
)
def compose_likec4_dev(
        context: AssetExecutionContext,
        env_base: dict,
        build_likec4_dev: str,
) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "likec4_dev": {
                "container_name": "likec4-dev-10-2",
                "hostname": "likec4-dev-10-2",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_likec4_dev,
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": [
                    "--host",
                    env_base.get('LIKEC4_HOST'),
                    "--port",
                    env_base.get('LIKEC4_DEV_PORT_CONTAINER'),
                ],
                "volumes": [
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}",
                ],
                "ports": [
                    f"{env_base.get('LIKEC4_DEV_PORT_HOST')}:{env_base.get('LIKEC4_DEV_PORT_CONTAINER')}",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_generic_runner_image_10_2": AssetIn(),
    },
)
def compose_rcs_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_generic_runner_image_10_2: str,
) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "deadline-rcs-runner-10-2": {
                "container_name": "deadline-rcs-runner-10-2",
                "hostname": "likec4-dev-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_generic_runner_image_10_2,
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": [
                    "--executable", "/opt/Thinkbox/Deadline10/bin/deadlinercs",
                ],
                "volumes": [
                    f"/home/michael/git/repos/deadline-docker/10.2/configs/Deadline10/deadline.ini:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/Deadline10:/opt/Thinkbox/Deadline10",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/DeadlineRepository10:/opt/Thinkbox/DeadlineRepository10",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
                ],
                "ports": [
                    f"{env_10_2.get('RCS_HTTP_PORT_HOST')}:{env_10_2.get('RCS_HTTP_PORT_CONTAINER')}",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "compose_rcs_runner_10_2": AssetIn(),
        "compose_repository_10_2": AssetIn(),
        "compose_networks_10_2": AssetIn(),
        "compose_mongo_express_10_2": AssetIn(),
        "compose_mongodb_10_2": AssetIn(),
        "compose_filebrowser_10_2": AssetIn(),
        "compose_dagster_dev": AssetIn(),
        "compose_likec4_dev": AssetIn(),
    },
)
def compose_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        compose_rcs_runner_10_2: dict,
        compose_repository_10_2: dict,
        compose_networks_10_2: dict,
        compose_mongo_express_10_2: dict,
        compose_mongodb_10_2: dict,
        compose_filebrowser_10_2: dict,
        compose_dagster_dev: dict,
        compose_likec4_dev: dict,
        # build_likec4_dev: str,
        # base_services_10_2: dict,
) -> pathlib.Path:
    """
    """

    docker_chainmap = ChainMap(
        compose_likec4_dev,
        compose_dagster_dev,
        compose_mongodb_10_2,
        compose_filebrowser_10_2,
        compose_mongo_express_10_2,
        compose_rcs_runner_10_2,
        compose_repository_10_2,
        compose_networks_10_2,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)
    docker_yaml = yaml.dump(docker_dict)

    docker_compose = pathlib.Path(
        f"/home/michael/git/repos/deadline-docker/10.2/.docker/docker_compose/{context.asset_key.path[0]}/docker-compose.yaml",
    )
    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    cmd_docker_compose_up = f"/usr/bin/docker compose -f {docker_compose} -p {context.asset_key.path[0]} up --remove-orphans"
    cmd_docker_compose_down = f"/usr/bin/docker compose -f {docker_compose} -p {context.asset_key.path[0]} down --remove-orphans"

    yield Output(docker_compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            # context.asset_key.path[0]: MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            context.asset_key.path[0]: MetadataValue.path(docker_compose),
            "docker_compose": MetadataValue.path(docker_compose),
            "cmd_docker_compose_up": MetadataValue.path(cmd_docker_compose_up),
            # "cmd_docker_compose_down": MetadataValue.path(cmd_docker_compose_down),
            "maps": MetadataValue.md(f"```json\n{json.dumps(docker_chainmap.maps, indent=2)}\n```"),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Viz",
    compute_kind="python",
    ins={
        "compose_10_2": AssetIn(),
    },
)
def viz_compose_10_2(
        context: AssetExecutionContext,
        compose_10_2: pathlib.Path,
):
    """
    """

    from docker_graph.docker_graph import DockerComposeGraph


    dcg = DockerComposeGraph()
    trees = dcg.parse_docker_compose(
        pathlib.Path(compose_10_2)
    )

    context.log.info(trees)

    dcg.iterate_trees(trees)

    dcg.graph.write(
        path=compose_10_2.parent / "main_graph.png",
        format="png",
    )

    # self.graph.write(
    #     path=pathlib.Path(__file__).parent.parent.parent / "tests" / "fixtures" / "out" / "main_graph.dot",
    #     format="dot",
    # )

    yield Output(None)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(compose_10_2.parent / "main_graph.png"),
            # "docker_compose": MetadataValue.path(docker_compose),
            # "cmd_docker_compose_up": MetadataValue.path(cmd_docker_compose_up),
            # # "cmd_docker_compose_down": MetadataValue.path(cmd_docker_compose_down),
            # "maps": MetadataValue.md(f"```json\n{json.dumps(docker_chainmap.maps, indent=2)}\n```"),
            # "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            # "env_base": MetadataValue.json(env_10_2),
        },
    )



"""
from docker_graph.docker_graph import main, DockerComposeGraph


dcg = DockerComposeGraph()
trees = dcg.parse_docker_compose(
    pathlib.Path("~/git/repos/docker-graph/tests/fixtures/deadline-docker/10.2/docker-compose.yaml")
)

# resolve environment variables (optional)
dcg.load_dotenv(pathlib.Path("/home/michael/git/repos/docker-graph/tests/fixtures/deadline-docker/10.2/.env"))

# dcg.expand_vars(tree)

# with open("tree.json", "w") as fw:
#     json.dump(tree, fw, indent=2)

dcg.iterate_trees(trees)
# dcg.connect()
dcg.write_png()
dcg.write_dot()
"""