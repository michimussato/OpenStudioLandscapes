import json
import pathlib
import time
import yaml
from collections import ChainMap
from functools import reduce

from python_on_whales import docker

from dagster import (AssetExecutionContext,
                     asset,
                     Output,
                     AssetMaterialization,
                     MetadataValue,
                     AssetIn)

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
        buildargs,
) -> dict[str, MetadataValue]:
    cmd_docker_run = f"docker run --rm -it --entrypoint bash {tag}"
    _cmd_docker_build_buildargs = ' '.join(f"--build-arg {k}={v}" for k, v in buildargs.items())
    cmd_docker_build = (f"docker build --tag {tag} {_cmd_docker_build_buildargs} {docker_file.parent.as_posix()} "
                        f"{'--no-cache' if USE_CACHE else ''}")

    metadata_values = {
        "cmd_docker_run": MetadataValue.path(cmd_docker_run),
        "cmd_docker_build": MetadataValue.path(cmd_docker_build),
    }

    return metadata_values


@asset(
    group_name="Environment"
)
def env_base(
        context: AssetExecutionContext,
) -> dict:
    _env: dict = {
        "MONGO_EXPRESS_PORT_HOST": "8181",
        "MONGO_EXPRESS_PORT_CONTAINER": "8081",
        # "MONGO_DB_NAME": "deadline10db",

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

        # "RCS_HTTP_PORT_HOST": 8888,
        "RCS_HTTP_PORT_CONTAINER": "8888",

        # "WEBSERVICE_HTTP_PORT_HOST": 8899,
        "WEBSERVICE_HTTP_PORT_CONTAINER": "8899",

        "MONGO_DB_PORT_HOST": "21017",
        "MONGO_DB_PORT_CONTAINER": "21017",
        # "MONGO_PORT": "${MONGO_DB_PORT_CONTAINER}",
        # # https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/#additional
        # -information-1
        # "ME_CONFIG_BASICAUTH_USERNAME": "web",
        # "ME_CONFIG_BASICAUTH_PASSWORD": "web",
        # "ME_CONFIG_OPTIONS_EDITORTHEME": "darcula",
        # "ME_CONFIG_MONGODB_SERVER": "mongodb-10-2",
        # "ME_CONFIG_MONGODB_URL": "mongodb://admin:pass@localhost:${MONGO_DB_PORT_CONTAINER}/db?ssl=false",
        #
        # "AYON_PORT_HOST": 5005,
        # "AYON_PORT_CONTAINER": 5000,
        #
        # "KITSU_PORT_HOST": 8181,
        # "KITSU_PORT_CONTAINER": 80,
        # #"SECRETS_USERNAME": "SecretsAdmin",
        # #"SECRETS_PASSWORD": "%ecretsPassw0rd!",
        "ROOT_DOMAIN": "farm.evil",
        # "DB_HOST": "mongodb-10-2",

        "GOOGLE_API_KEY": "AIzaSyBBH8zUH4VC1Bov-3EdVbjG0gBauroMd9E",

        # "PYTHON_VERSION": "3.11.11",
        "PYTHON_MAJ": "3",
        "PYTHON_MIN": "11",
        "PYTHON_PAT": "11",

        "NFS_ENTRY_POINT": "/data/share/nfs",
        "NFS_ENTRY_POINT_LNS": "/nfs",
        "INSTALLERS_ROOT": "/data/share/nfs/installers",

        # # TODO
        # # DEADLINE_INI:
        # # DEADLINE_CLIENT_DIR: "/opt/Thinkbox/Deadline10"
        # # DEADLINE_REPO_DIR: "/opt/Thinkbox/DeadlineRepository10"
        # # MONGO_DB_NAME: deadline10db
        # # MONGO_DB_HOST: $DB_HOST
        # # MONGO_DB_PROD:
        # # MONGO_DB_TEST:
    }

    yield Output(_env)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(_env),

        },
    )


@asset(
    group_name="Environment_10_2",
    ins={
        "env_base": AssetIn(),
    },
    deps=[
        "build_base_image",
    ],
)
def env_10_2(
        context: AssetExecutionContext,
        env_base: dict,
) -> dict:
    _env: dict = {
        "DEADLINE_VERSION": "10.2.1.1",

        "GOOGLE_ID_AWSPortalLink_10_2": "1VOQa6OyYUZj_7VILcD6EVl7YOfYVlCrU",
        "GOOGLE_ID_DeadlineClient_10_2": "1cGxCPkrJ1ujWqie2yXTrOpShkEgSXR0F",
        "GOOGLE_ID_DeadlineRepository_10_2": "1VZhCcxvCAc4oozLAKRCv_zwQLMuVdMRz",
    }

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

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/Dockerfile")
    tags = [
        "michimussato/base_image:latest",
        f"michimussato/base_image:{str(time.time())}",
    ]
    buildargs = {
        "PYTHON_MAJ": env_base.get("PYTHON_MAJ"),
        "PYTHON_MIN": env_base.get("PYTHON_MIN"),
        "PYTHON_PAT": env_base.get("PYTHON_PAT"),
    }

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    context.log.info(f"{buildargs = }")

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        build_args=buildargs,
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
        buildargs=buildargs,
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
    ins={
        "env_10_2": AssetIn(),
    },
    deps=[
        "build_base_image",
    ],
)
def build_base_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        "/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/base_image_10_2/Dockerfile")

    context.log.info(f"{docker_file.as_posix() = }")

    tags = [
        "michimussato/base_image_10_2:latest",
        f"michimussato/base_image_10_2:{str(time.time())}",
    ]
    buildargs = {
        "PYTHON_MAJ": env_10_2.get("PYTHON_MAJ"),
        "PYTHON_MIN": env_10_2.get("PYTHON_MIN"),
        "PYTHON_PAT": env_10_2.get("PYTHON_PAT"),
        "GOOGLE_API_KEY": env_10_2.get("GOOGLE_API_KEY"),
        "GOOGLE_ID_AWSPortalLink_10_2": env_10_2.get("GOOGLE_ID_AWSPortalLink_10_2"),
        "GOOGLE_ID_DeadlineClient_10_2": env_10_2.get("GOOGLE_ID_DeadlineClient_10_2"),
        "GOOGLE_ID_DeadlineRepository_10_2": env_10_2.get("GOOGLE_ID_DeadlineRepository_10_2"),
    }

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    context.log.info(f"{buildargs = }")

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        build_args=buildargs,
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
        buildargs=buildargs,
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
    ins={
        "env_10_2": AssetIn(),
    },
    deps=[
        "build_base_image_10_2"
    ],
)
def build_repository_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        "/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/base_image_10_2/repo_installer/Dockerfile")
    tags = [
        "michimussato/repository_image_10_2:latest",
        f"michimussato/repository_image_10_2:{str(time.time())}",
    ]
    buildargs = {
        "DEADLINE_VERSION": env_10_2.get("DEADLINE_VERSION"),
        "MONGO_DB_PORT_HOST": env_10_2.get("MONGO_DB_PORT_HOST"),
    }

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    context.log.info(f"{buildargs = }")

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        build_args=buildargs,
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
        buildargs=buildargs,
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
    ins={
        "env_10_2": AssetIn(),
    },
    deps=[
        "build_base_image_10_2"
    ],
)
def build_client_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        "/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/base_image_10_2/client_installer"
        "/Dockerfile")
    tags = [
        "michimussato/client_image_10_2:latest",
        f"michimussato/client_image_10_2:{str(time.time())}",
    ]
    buildargs = {
        "DEADLINE_VERSION": env_10_2.get("DEADLINE_VERSION"),
        "RCS_HTTP_PORT_CONTAINER": env_10_2.get("RCS_HTTP_PORT_CONTAINER"),
        "WEBSERVICE_HTTP_PORT_CONTAINER": env_10_2.get("WEBSERVICE_HTTP_PORT_CONTAINER"),
    }

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    context.log.info(f"{buildargs = }")

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        build_args=buildargs,
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
        buildargs=buildargs,
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
    ins={
        "env_base": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def build_dagster_dev(
        context: AssetExecutionContext,
        env_base: dict,
) -> str:
    """
    """

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/dagster_dev/Dockerfile")
    tags = [
        "michimussato/dagster_dev:latest",
        f"michimussato/dagster_dev:{str(time.time())}",
    ]
    buildargs = {
        "PYTHON_MAJ": env_base.get("PYTHON_MAJ"),
        "PYTHON_MIN": env_base.get("PYTHON_MIN"),
        "DAGSTER_DAGSTER_WORKSPACE": env_base.get("DAGSTER_DAGSTER_WORKSPACE"),
        "DAGSTER_HOME": env_base.get("DAGSTER_HOME"),
    }

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    context.log.info(f"{buildargs = }")

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        # docker_file=docker_file.as_posix(),
        build_args=buildargs,
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
        buildargs=buildargs,
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
    ins={
        "env_base": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def build_likec4_dev(
        context: AssetExecutionContext,
        env_base: dict,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        "/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/likec4_dev/Dockerfile")
    tags = [
        "michimussato/likec4_dev:latest",
        f"michimussato/likec4_dev:{str(time.time())}",
    ]
    buildargs = {}

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    context.log.info(f"{buildargs = }")

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        build_args=buildargs,
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
        buildargs=buildargs,
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
#     group_name="Services",
#     ins={
#         "env_base": AssetIn(),
#     },
#     # deps=[
#     #     "build_base_image"
#     # ],
# )
# def filebrowser(
#         context: AssetExecutionContext,
#         env_base: dict,
# ) -> int:
#     """
#     """
#
#     client = docker.from_env()
#
#     container = client.containers.run(
#         image="filebrowser/filebrowser",
#         detach=True,
#         # remove=True,
#         # volumes={
#         #     "/home/michael/git/repos/deadline-docker/10.2/databases/filebrowser/filebrowser.db": {
#         #         "bind": "/filebrowser.db",
#         #         "mode": "rw",
#         #     },
#         #     "/home/michael/git/repos/deadline-docker/10.2/configs/filebrowser/filebrowser.json": {
#         #         "bind": "/filebrowser.json",
#         #         "mode": "rw",
#         #     },
#         # },
#         volumes=[
#             # "/home/michael/git/repos/deadline-docker/10.2/databases/filebrowser/filebrowser.db:/database
#             /filebrowser.db",
#             # "/home/michael/git/repos/deadline-docker/10.2/configs/filebrowser/filebrowser.json:/config/settings
#             .json",
#             # "/data/share/nfs:/data/share/nfs:ro",
#             # "/data/share/nfs:/nfs:ro",
#             "/data/share/nfs:/srv:ro",
#         ],
#         domainname="farm.evil",
#         hostname="mongo-filebrowser-10-2",
#         name="mongo-filebrowser-10-2",
#         restart_policy={
#             "Name": "always",
#         },
#         # ports={
#         #     "8080": 80,
#         # },
#         # network="repository",
#     )
#
#     # network = client.networks.create(
#     #     name="repository",
#     #     driver="bridge",
#     # )
#     #
#     # network.connect(
#     #     container=container,
#     # )
#
#     context.log.info(dir(container))
#
#     # docker_file = pathlib.Path(
#     #     "/home/michael/git/repos/deadline-docker/10.2/base_images/base_image/likec4_dev/Dockerfile")
#     # tag = "michimussato/likec4_dev:latest"
#     # buildargs = {}
#     #
#     # with open(docker_file, "r") as fr:
#     #     context.log.info(fr.read())
#     #
#     # base_image, build_logs = docker_build(
#     #     docker_file=docker_file,
#     #     tag=tag,
#     #     buildargs=buildargs,
#     #     nocache=True,
#     # )
#
#     # cmds_docker = compile_cmds(
#     #     docker_file=docker_file,
#     #     tag=tag,
#     #     buildargs=buildargs,
#     # )
#
#     yield Output(80)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             context.asset_key.path[0]: MetadataValue.int(80),
#             "url": MetadataValue.url("http://localhost:80/"),
#             "docker_file": MetadataValue.json(container.id),
#             # **cmds_docker,
#             # "build_logs": MetadataValue.md(f"```shell\n{get_log(build_logs)}\n```"),
#             "env_base": MetadataValue.json(env_base),
#         },
#     )

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

# @asset(
#     group_name="Docker_Swarm",
#     ins={
#         "env_10_2": AssetIn(),
#     }
# )
# def docker_swarm(
#         context: AssetExecutionContext,
#         env_10_2: dict,
# ) -> str:
#
#     client = docker.from_env()
#     swarm = client.swarm.init(
#         advertise_addr='192.168.100.69',
#         listen_addr='0.0.0.0:5000',
#         force_new_cluster=False,
#         default_addr_pool=['10.1.2.0/24'],
#         subnet_size=24,
#         snapshot_interval=5000,
#         log_entries_for_slow_followers=1200
#     )
#
#     yield Output(swarm)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "swarm_id": MetadataValue.json(swarm),
#             "env_10_2": MetadataValue.json(env_10_2),
#         },
#     )


# @asset(
#     group_name="Services",
#     ins={
#         "docker_swarm": AssetIn(),
#     },
# )
# def mongo_db(
#         context: AssetExecutionContext,
#         docker_swarm: str,
# ):
#     client = docker.from_env()
#
#     client.swarm.join(docker_swarm)
#
#     service = client.services.create(
#         container_name="mongodb-10-2",
#         hostname="mongodb-10-2",
#         # domainname=
#         image="mongodb/mongodb-community-server:4.4-ubuntu2004",
#         name="mongodb-10-2",
#         networks=[],
#         env=[],
#         # restart_policy=RestartPolicy.a,
#         command=[
#             "--dbpath", "/opt/Thinkbox/DeadlineDatabase10/mongo/data",
#             "--bind_ip_all",
#             "--noauth",
#             "--storageEngine", "wiredTiger",
#             "--tlsMode", "disabled",
#         ],
#         mounts=[
#             "${NFS_ENTRY_POINT}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL:/opt/Thinkbox
#             /DeadlineDatabase10/mongo/data",
#             "${NFS_ENTRY_POINT}:${NFS_ENTRY_POINT}:ro",
#             "${NFS_ENTRY_POINT}:${NFS_ENTRY_POINT_LNS}:ro",
#         ],
#         # ports
#     )
#
#     yield Output(service.id)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "service_id": MetadataValue.json(service.id),
#             "service_name": MetadataValue.json(service.name),
#             "env_10_2": MetadataValue.json(env_10_2),
#         },
#     )


@asset(
    group_name="Docker_Compose_10_2",
    ins={
        "env_base": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def compose_networks_10_2(
        context: AssetExecutionContext,
        env_base: dict,
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
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    ins={
        "env_base": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def compose_mongo_express_10_2(
        context: AssetExecutionContext,
        env_base: dict,
) -> dict:
    docker_dict = {
        "services": {
            "mongo-express-10-2": {
                "image": "mongo-express",
                "hostname": "mongo-express-10-2",
                "container_name": "mongo-express-10-2",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "restart": "always",
                "depends_on": [
                    "mongodb-10-2",
                ],
                "networks": [
                    "mongodb",
                ],
                "ports": [
                    f"{env_base.get('MONGO_EXPRESS_PORT_HOST')}:{env_base.get('MONGO_EXPRESS_PORT_CONTAINER')}",
                ],
                "volumes": [
                    f"{env_base.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL"
                    f":/opt/Thinkbox/DeadlineDatabase10/mongo/data",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}:ro",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}:ro",
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
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    ins={
        "env_base": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def compose_filebrowser_10_2(
        context: AssetExecutionContext,
        env_base: dict,
) -> dict:
    docker_dict = {
        "services": {
            "filebrowser": {
                "image": "filebrowser/filebrowser",
                "container_name": "filebrowser-10-2",
                "hostname": "filebrowser-10-2",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "restart": "always",
                # "depends_on": [
                #     "mongodb-10-2",
                # ],
                "networks": [
                    "repository",
                ],
                "ports": [
                    f"{env_base.get('FILEBROWSER_PORT_HOST')}:{env_base.get('FILEBROWSER_PORT_CONTAINER')}",
                ],
                "volumes": [
                    "/home/michael/git/repos/deadline-docker/10.2/databases/filebrowser/filebrowser.db:/filebrowser.db",
                    "/home/michael/git/repos/deadline-docker/10.2/configs/filebrowser/filebrowser.json:/.filebrowser.json",
                    f"{env_base.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL"
                    f":/opt/Thinkbox/DeadlineDatabase10/mongo/data:ro",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}:ro",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}:ro",
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
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    ins={
        "env_base": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def compose_mongodb_10_2(
        context: AssetExecutionContext,
        env_base: dict,
) -> dict:
    docker_dict = {
        "services": {
            "mongodb-10-2": {
                "image": "mongodb/mongodb-community-server:4.4-ubuntu2004",
                "container_name": "mongodb-10-2",
                "hostname": "mongodb-10-2",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "restart": "always",
                # "depends_on": [],
                "command": [
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
                    f"{env_base.get('MONGO_DB_PORT_HOST')}:{env_base.get('MONGO_DB_PORT_CONTAINER')}",
                ],
                "volumes": [
                    f"{env_base.get('NFS_ENTRY_POINT')}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL"
                    f":/opt/Thinkbox/DeadlineDatabase10/mongo/data",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}:ro",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}:ro",
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
            "env_base": MetadataValue.json(env_base),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    ins={
        "env_base": AssetIn(),
        "build_dagster_dev": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
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
    ins={
        "env_base": AssetIn(),
        "build_likec4_dev": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
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
    ins={
        "env_base": AssetIn(),
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
        env_base: dict,
        compose_networks_10_2: dict,
        compose_mongo_express_10_2: dict,
        compose_mongodb_10_2: dict,
        compose_filebrowser_10_2: dict,
        compose_dagster_dev: dict,
        compose_likec4_dev: dict,
        # build_likec4_dev: str,
        # base_services_10_2: dict,
) -> ChainMap:
    """
    """

    docker_chainmap = ChainMap(
        compose_likec4_dev,
        compose_dagster_dev,
        compose_mongodb_10_2,
        compose_filebrowser_10_2,
        compose_mongo_express_10_2,
        compose_networks_10_2,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)
    docker_yaml = yaml.dump(docker_dict)

    docker_compose = pathlib.Path(f"/home/michael/git/repos/deadline-docker/10.2/.docker_compose/{context.asset_key.path[0]}/docker-compose.yaml")
    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    yield Output(docker_chainmap)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_compose": MetadataValue.path(docker_compose),
            "maps": MetadataValue.md(f"```json\n{json.dumps(docker_chainmap.maps, indent=2)}\n```"),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_base": MetadataValue.json(env_base),
        },
    )
