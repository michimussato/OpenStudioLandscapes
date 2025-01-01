import pathlib

import docker

from dagster import (AssetExecutionContext,
                     asset,
                     Output,
                     AssetMaterialization,
                     MetadataValue,
                     AssetIn)


@asset(
    group_name="Environment"
)
def env(
        context: AssetExecutionContext,
) -> dict:
    _env: dict = {
        # "MONGO_EXPRESS_PORT_HOST": 8080,
        # "MONGO_EXPRESS_PORT_CONTAINER": 8081,
        # "MONGO_DB_NAME": "deadline10db",

        # "LIKEC4_DEV_PORT_HOST": 4567,
        # "LIKEC4_DEV_PORT_CONTAINER": 4567,

        # "FILEBROWSER_PORT_HOST": 86,
        # "FILEBROWSER_PORT_CONTAINER": 80,

        # "DAGSTER_DEV_PORT_HOST": 3003,
        # "DAGSTER_DEV_PORT_CONTAINER": 3006,
        # "DAGSTER_HOME": "/dagster/materializations",
        # "DAGSTER_WORKSPACE": "/dagster/workspace.yaml",

        "DEADLINE_VERSION": "10.2.1.1",

        # "RCS_HTTP_PORT_HOST": 8888,
        # "RCS_HTTP_PORT_CONTAINER": 8888,
        #
        # "WEBSERVICE_HTTP_PORT_HOST": 8899,
        # "WEBSERVICE_HTTP_PORT_CONTAINER": 8899,
        #
        # "MONGO_DB_PORT_HOST": 21017,
        # "MONGO_DB_PORT_CONTAINER": 21017,
        # "MONGO_PORT": "${MONGO_DB_PORT_CONTAINER}",
        # # https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/#additional-information-1
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
        # "ROOT_DOMAIN": "farm.evil",
        # "DB_HOST": "mongodb-10-2",

        # "GOOGLE_API_KEY": "AIzaSyBBH8zUH4VC1Bov-3EdVbjG0gBauroMd9E",
        # "GOOGLE_ID": "1VZhCcxvCAc4oozLAKRCv_zwQLMuVdMRz",

        # "PYTHON_VERSION": "3.11.11",
        "PYTHON_MAJ": "3",
        "PYTHON_MIN": "11",
        "PYTHON_PAT": "11",

        # "NFS_ENTRY_POINT": "/data/share/nfs",
        # "NFS_ENTRY_POINT_LNS": "/nfs",
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

    return _env


@asset(
    group_name="Build_Images",
    ins={
        "env": AssetIn(),
    },
)
def build_base_image(
        context: AssetExecutionContext,
        env: dict,
):
    """
    docker build  \
    --tag michimussato/repo_base:latest  \
    --build-arg PYTHON_MAJ=3  \
    --build-arg PYTHON_MIN=11  \
    --build-arg PYTHON_PAT=11  \
    .
    """

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/repo_base/Dockerfile")
    tag = "michimussato/repo_base:latest"
    buildargs = {
        "PYTHON_MAJ": env.get("PYTHON_MAJ"),
        "PYTHON_MIN": env.get("PYTHON_MIN"),
        "PYTHON_PAT": env.get("PYTHON_PAT"),
    }

    client = docker.from_env()

    base_image, build_logs = client.images.build(
        path=docker_file.parent.as_posix(),
        tag=tag,
        buildargs=buildargs,
    )

    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                context.log.debug(line)

    yield Output(base_image.id)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "image_id": MetadataValue.json(base_image.id),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    group_name="Build_Images",
    ins={
        "env": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def build_repo_installer(
        context: AssetExecutionContext,
        env: dict,
):
    """
    docker build  \
    --tag michimussato/repo_installer:latest  \
    --build-arg DEADLINE_VERSION=10.2.1.1  \
    --build-arg INSTALLERS_ROOT=/data/share/nfs/installers  \
    .
    """

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/repo_base/repo_installer/Dockerfile")
    tag = "michimussato/repo_installer:latest"
    buildargs = {
        "DEADLINE_VERSION": env.get("DEADLINE_VERSION"),
        "INSTALLERS_ROOT": env.get("INSTALLERS_ROOT"),
    }

    client = docker.from_env()

    base_image, build_logs = client.images.build(
        path=docker_file.parent.as_posix(),
        tag=tag,
        buildargs=buildargs,
    )

    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                context.log.debug(line)

    yield Output(base_image.id)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "image_id": MetadataValue.json(base_image.id),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    group_name="Build_Images",
    ins={
        "env": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def build_client_installer(
        context: AssetExecutionContext,
        env: dict,
):
    """
docker build  \
    --tag michimussato/client_installer:latest  \
    --build-arg DEADLINE_VERSION=10.2.1.1  \
    --build-arg INSTALLERS_ROOT=/data/share/nfs/installers  \
    .
    """

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/repo_base/client_installer/Dockerfile")
    tag = "michimussato/client_installer:latest"
    buildargs = {
        "DEADLINE_VERSION": env.get("DEADLINE_VERSION"),
        "INSTALLERS_ROOT": env.get("INSTALLERS_ROOT"),
    }

    client = docker.from_env()

    base_image, build_logs = client.images.build(
        path=docker_file.parent.as_posix(),
        tag=tag,
        buildargs=buildargs,
    )

    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                context.log.debug(line)

    yield Output(base_image.id)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "image_id": MetadataValue.json(base_image.id),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    group_name="Build_Images",
    ins={
        "env": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def build_dagster_dev(
        context: AssetExecutionContext,
        env: dict,
):
    """
docker build  \
    --tag michimussato/dagster_dev:latest  \
    --build-arg PYTHON_MAJ=3  \
    --build-arg PYTHON_MIN=11  \
    --build-arg PYTHON_PAT=11  \
    .
    """

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/repo_base/dagster_dev/Dockerfile")
    tag = "michimussato/dagster_dev:latest"
    buildargs = {
        "PYTHON_MAJ": env.get("PYTHON_MAJ"),
        "PYTHON_MIN": env.get("PYTHON_MIN"),
        "PYTHON_PAT": env.get("PYTHON_PAT"),
    }

    client = docker.from_env()

    base_image, build_logs = client.images.build(
        path=docker_file.parent.as_posix(),
        tag=tag,
        buildargs=buildargs,
    )

    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                context.log.debug(line)

    yield Output(base_image.id)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "image_id": MetadataValue.json(base_image.id),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    group_name="Build_Images",
    ins={
        "env": AssetIn(),
    },
    deps=[
        "build_base_image"
    ],
)
def build_likec4_dev(
        context: AssetExecutionContext,
        env: dict,
):
    """
docker build  \
    --tag michimussato/likec4_dev:latest  \
    .
    """

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/repo_base/likec4_dev/Dockerfile")
    tag = "michimussato/likec4_dev:latest"
    buildargs = {
    }

    client = docker.from_env()

    base_image, build_logs = client.images.build(
        path=docker_file.parent.as_posix(),
        tag=tag,
        buildargs=buildargs,
    )

    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                context.log.debug(line)

    yield Output(base_image.id)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "image_id": MetadataValue.json(base_image.id),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    group_name="Build_Images",
    ins={
        "env": AssetIn(),
    },
    deps=[
        "build_client_installer"
    ],
)
def build_generic_runner(
        context: AssetExecutionContext,
        env: dict,
):
    """
docker build  \
    --tag michimussato/generic_runner:latest  \
    .
    """

    docker_file = pathlib.Path("/home/michael/git/repos/deadline-docker/10.2/base_images/repo_base/client_installer/generic_runner/Dockerfile")
    tag = "michimussato/generic_runner:latest"
    buildargs = {
    }

    client = docker.from_env()

    base_image, build_logs = client.images.build(
        path=docker_file.parent.as_posix(),
        tag=tag,
        buildargs=buildargs,
    )

    for chunk in build_logs:
        if 'stream' in chunk:
            for line in chunk['stream'].splitlines():
                context.log.debug(line)

    yield Output(base_image.id)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "image_id": MetadataValue.json(base_image.id),
            "env": MetadataValue.json(env),
        },
    )


# @asset(
#     group_name="Docker_Swarm",
#     ins={
#         "env": AssetIn(),
#     }
# )
# def docker_swarm(
#         context: AssetExecutionContext,
#         env: dict,
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
#             "env": MetadataValue.json(env),
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
#             "${NFS_ENTRY_POINT}/test_data/10.2/opt/Thinkbox/DeadlineDatabase10/mongo/data_LOCAL:/opt/Thinkbox/DeadlineDatabase10/mongo/data",
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
#             "env": MetadataValue.json(env),
#         },
#     )
