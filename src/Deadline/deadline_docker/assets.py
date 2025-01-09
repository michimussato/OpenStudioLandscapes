import json
import shutil
import textwrap
import pathlib
import time
import yaml
import pydot
from collections import ChainMap
from functools import reduce

from python_on_whales import docker
from docker_graph.docker_graph import DockerComposeGraph

from dagster import (
    AssetExecutionContext,
    asset,
    Output,
    AssetMaterialization,
    MetadataValue,
    AssetIn,
)

USE_CACHE = False


# class SelfRefDict(dict):
#     def __getitem__(self, item):
#         return dict.__getitem__(self, item).format(self)


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
        volumes: [list, None] = None,
        networks: [list, None] = None,
) -> dict[str, MetadataValue]:

    if volumes is None:
        volumes = []

    if networks is None:
        networks = []

    _volumes = ' '.join([f'--volume {i}' for i in volumes])
    _networks = ' '.join([f'--network {i}' for i in networks])

    cmd_docker_run = f"docker run {_volumes} {_networks} --rm --interactive --tty --entrypoint bash {tag}"
    cmd_docker_build = (
        f"docker build --tag {tag} {docker_file.parent.as_posix()} {'--no-cache' if USE_CACHE else ''}"
    )

    metadata_values = {
        "cmd_docker_run": MetadataValue.path(cmd_docker_run),
        "cmd_docker_build": MetadataValue.path(cmd_docker_build),
    }

    return metadata_values


def docker_cleanup(
        context: AssetExecutionContext = None,
):
    """
from Deadline.deadline_docker.assets import docker_cleanup
docker_cleanup()
    """
    # out = {
    #     "stdout": context.log.info,
    #     "stderr": context.log.error,
    # }

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

        "LIKEC4_DEV_PORT_HOST": "4567",
        "LIKEC4_DEV_PORT_CONTAINER": "4567",
        "LIKEC4_HOST": "0.0.0.0",

        "FILEBROWSER_PORT_HOST": "8080",
        "FILEBROWSER_PORT_CONTAINER": "80",
        "FILEBROWSER_DB": pathlib.Path("~/git/repos/deadline-docker/10.2/databases/filebrowser/filebrowser.db").expanduser().as_posix(),
        "FILEBROWSER_JSON": pathlib.Path("~/git/repos/deadline-docker/10.2/configs/filebrowser/filebrowser.json").expanduser().as_posix(),

        "DAGSTER_DEV_PORT_HOST": "3003",
        "DAGSTER_DEV_PORT_CONTAINER": "3006",
        "DAGSTER_ROOT": "/dagster",
        "DAGSTER_HOME": "/dagster/materializations",
        "DAGSTER_HOST": "0.0.0.0",
        "DAGSTER_WORKSPACE": "/dagster/workspace.yaml",

        "RCS_HTTP_PORT_HOST": "8888",
        "RCS_HTTP_PORT_CONTAINER": "8888",

        "WEBSERVICE_HTTP_PORT_HOST": "8899",
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
        # Todo:
        #  - [ ] Verify whether MONGO_DB_PORT_CONTAINER or MONGO_DB_PORT_HOST
        #        is actually correct
        "ME_CONFIG_MONGODB_URL": "mongodb://admin:pass@localhost:{MONGO_DB_PORT_CONTAINER}/db?ssl=false",

        # "AYON_PORT_HOST": 5005,
        # "AYON_PORT_CONTAINER": 5000,

        "KITSU_PORT_HOST": "4545",
        "KITSU_PORT_CONTAINER": "80",
        "KITSU_POSTGRESQL_CONF": pathlib.Path("~/git/repos/deadline-docker/10.2/configs/kitsu/postgres/postgresql.conf").expanduser().as_posix(),
        # #"SECRETS_USERNAME": "SecretsAdmin",
        # #"SECRETS_PASSWORD": "%ecretsPassw0rd!",
        "ROOT_DOMAIN": "farm.evil",
        # "DB_HOST": "mongodb-10-2",

        # "PYTHON_VERSION": "3.11.11",
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
        # "MONGO_DB_DIR": pathlib.Path("~/git/repos/deadline-docker/tests/fixtures/10.2/DeadlineDatabase10/mongo/data").expanduser().as_posix(),
        # "DEADLINE_CLIENT_DEADLINE_INI": pathlib.Path("~/git/repos/deadline-docker/10.2/configs/Deadline10/deadline.ini").expanduser().as_posix(),

        # # TEST
        "LN_NFS": "/nfs",
        "NFS_ENTRY_POINT": "/data/share/nfs",
        "NFS_ENTRY_POINT_LNS": "/nfs",
        "INSTALLERS_ROOT": "/data/share/nfs/installers",
        "NFS_REPOSITORY": "/data/share/nfs/test_data/10.2/opt/Thinkbox/DeadlineRepository10",
        "NFS_DEADLINE": "/data/share/nfs/test_data/10.2/opt/Thinkbox/Deadline10",
        "MONGO_DB_DIR": pathlib.Path("~/git/repos/deadline-docker/tests/fixtures/10.2/DeadlineDatabase10/mongo/data").expanduser().as_posix(),
        "DEADLINE_CLIENT_DEADLINE_INI": pathlib.Path("~/git/repos/deadline-docker/10.2/configs/Deadline10/deadline.ini").expanduser().as_posix(),
        "DEADLINE_REPOSITORY_CONNECTION_INI": pathlib.Path("~/git/repos/deadline-docker/10.2/configs/DeadlineRepository10/settings/connection.ini").expanduser().as_posix(),

        # # TODO
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

        "MONGO_DB_HOST": "mongodb-10-2",

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
    group_name="Settings_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
    },
)
def connection_ini_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> pathlib.Path:
    # @formatter:off
    connection_ini = textwrap.dedent("""
    # {auto_generated}
    [Connection]
    AlternatePort=0
    Authenticate=False
    DatabaseName={MONGO_DB_NAME}
    DbType=MongoDB
    EnableSSL=False
    Hostname={MONGO_DB_HOST}
    PasswordHash=
    Port={MONGO_DB_PORT_CONTAINER}
    ReplicaSetName=
    SplitDB=False
    Username=
    Version=10
    StorageAccess=Database
    CACertificatePath=
    ClientsThatPreferSecondaryReplicas=
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
        **env_10_2,
    )
    # @formatter:on

    with open(env_10_2.get("DEADLINE_REPOSITORY_CONNECTION_INI"), "w") as fw:
        fw.write(connection_ini)

    ret = pathlib.Path(env_10_2.get("DEADLINE_REPOSITORY_CONNECTION_INI"))

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(ret),
            "connection_ini": MetadataValue.md(f"```\n{connection_ini}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Settings_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
    },
)
def deadline_ini_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> pathlib.Path:
    # @formatter:off
    deadline_ini = textwrap.dedent("""
    # {auto_generated}
    # Full Documentation
    # https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/manual/client-config.html#client-config-conn-server-ref-label
    [Deadline]
    # # For Remote
    # ConnectionType=Remote
    # ProxyRoot=rcs-runner-10-2:8888
    # ProxyRoot0=rcs-runner-10-2:8888
    # ###
    # #################################
    # For Repository
    ConnectionType=Repository
    NetworkRoot=/opt/Thinkbox/DeadlineRepository10
    NetworkRoot0=/opt/Thinkbox/DeadlineRepository10
    ###
    WebServiceHttpListenPort={WEBSERVICE_HTTP_PORT_CONTAINER}
    WebServiceTlsListenPort=0
    WebServiceTlsServerCert=
    WebServiceTlsCaCert=
    WebServiceTlsAuth=False
    WebServiceClientSSLAuthentication=NotRequired
    HttpListenPort={RCS_HTTP_PORT_CONTAINER}
    TlsListenPort=0
    LicenseMode=LicenseFree
    Region=
    LauncherListeningPort=17000
    LauncherServiceStartupDelay=60
    AutoConfigurationPort=17001
    SlaveStartupPort=17003
    LicenseForwarderListeningPort=17004
    SlaveDataRoot=
    NoGuiMode=false
    AutoUpdateOverride=false
    IncludeRCSInLauncherMenu=true
    DbSSLCertificate=
    AutoUpdateBlock=NotBlocked
    
    # Controlled by Docker
    LaunchRemoteConnectionServerAtStartup=false
    KeepRemoteConnectionServerRunning=false
    LaunchPulseAtStartup=false
    KeepPulseRunning=false
    LaunchBalancerAtStartup=false
    KeepBalancerRunning=false
    KeepWebServiceRunning=false
    KeepWorkerRunning=false
    RestartStalledSlave=false
    LaunchLicenseForwarderAtStartup=false
    KeepLicenseForwarderRunning=false
    LaunchSlaveAtStartup=false
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
        **env_10_2,
    )
    # @formatter:on

    with open(env_10_2.get("DEADLINE_CLIENT_DEADLINE_INI"), "w") as fw:
        fw.write(deadline_ini)

    ret = pathlib.Path(env_10_2.get("DEADLINE_CLIENT_DEADLINE_INI"))

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.path(ret),
            "connection_ini": MetadataValue.md(f"```\n{deadline_ini}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
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
        
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore "deadline-dagster @ git+https://github.com/michimussato/deadline-dagster.git@main"
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared @ git+https://github.com/michimussato/dagster-shared.git@main"
        # RUN thinkbox-ssl-gen --help
        
        RUN rm -rf /build/python
        
        RUN apt-get clean
        
        ENTRYPOINT []
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
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
        volumes=[],
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
        # {auto_generated}
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
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
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
        # {auto_generated}
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
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
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
        # {auto_generated}
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
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
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
        # {auto_generated}
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        SHELL ["/bin/bash", "-c"]
        
        ENTRYPOINT ["deadline-wrapper-10-2", "-vv", "run"]
        
        CMD ["--help"]
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
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
        volumes=[
            f"{env_10_2.get('DEADLINE_CLIENT_DEADLINE_INI')}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
            f"{env_10_2.get('DEADLINE_REPOSITORY_CONNECTION_INI')}:/opt/Thinkbox/DeadlineRepository10/settings"
            f"/connection.ini:ro",
            f"{env_10_2.get('NFS_REPOSITORY')}:/opt/Thinkbox/DeadlineRepository10",
            f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
            f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
        ],
        networks=[
            "network_repository-10-2",
            "network_mongodb-10-2",
        ],

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
        # {auto_generated}
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"
        
        WORKDIR {DAGSTER_ROOT}
        COPY ./payload/workspace.yaml .
        
        WORKDIR {DAGSTER_HOME}
        COPY ./payload/dagster.yaml .
        
        WORKDIR {DAGSTER_ROOT}
        
        ENTRYPOINT ["dagster", "dev"]
        CMD []
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
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
        src=pathlib.Path("~/git/repos/deadline-docker/10.2/configs/dagster_dev/config/workspace.yaml").expanduser(),
        dst=payload,
    )

    # dagster.yaml
    shutil.copy(
        src=pathlib.Path(
            "~/git/repos/deadline-docker/10.2/configs/dagster_dev/config/materializations/dagster.yaml"
            ).expanduser(),
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
        # "build_base_image": AssetIn(),
    },
)
def build_kitsu(
        context: AssetExecutionContext,
        env_base: dict,
        # build_base_image: str,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        f"~/git/repos/deadline-docker/.docker/Dockerfiles/{context.asset_key.path[0]}/Dockerfile"
    ).expanduser()

    tags = [
        f"michimussato/{context.asset_key.path[0]}:latest",
        f"michimussato/{context.asset_key.path[0]}:{str(time.time())}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # {auto_generated}
        # https://hub.docker.com/r/cgwire/cgwire
        FROM cgwire/cgwire:latest AS {image_name}
        LABEL authors="{AUTHOR}"
        
        #RUN tar -cvzf /var/lib/postgresql/14/main.tar.gz /var/lib/postgresql/14/main
        
        WORKDIR /opt/zou
        
        ENTRYPOINT ["/opt/zou/start_zou.sh"]
        CMD []
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
        image_name=context.asset_key.path[0],
        # parent_image=build_base_image,
        **env_base,
    )
    # @formatter:on

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_file, "w") as fw:
        fw.write(docker_file_str)

    # payload = docker_file.parent / "payload"
    # payload.mkdir(parents=True, exist_ok=True)
    #
    # # setup.sh
    # shutil.copy(
    #     src=pathlib.Path("~/git/repos/deadline-docker/10.2/configs/likec4_dev/entrypoint/setup.sh").expanduser(),
    #     dst=payload,
    # )
    #
    # # run.sh
    # shutil.copy(
    #     src=pathlib.Path("~/git/repos/deadline-docker/10.2/configs/likec4_dev/entrypoint/run.sh").expanduser(),
    #     dst=payload,
    # )

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
        # {auto_generated}
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
        auto_generated=f"AUTO-GENERATED by Dagster Asset {context.asset_key.path[0]}",
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
        src=pathlib.Path("~/git/repos/deadline-docker/10.2/configs/likec4_dev/entrypoint/setup.sh").expanduser(),
        dst=payload,
    )

    # run.sh
    shutil.copy(
        src=pathlib.Path("~/git/repos/deadline-docker/10.2/configs/likec4_dev/entrypoint/run.sh").expanduser(),
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
    group_name="Docker_Compose_10_2",
    compute_kind="python",
)
def compose_include_10_2(
        context: AssetExecutionContext,
        # env_10_2: dict,
) -> dict:
    docker_dict = {
        "include": [
            # {
            #     "path": [
            #         pathlib.Path("~/git/repos/deadline-docker/repos/ayon-docker/docker-compose.yml").expanduser().as_posix(),
            #         pathlib.Path("~/git/repos/deadline-docker/10.2/docker-third-party/ayon/docker-compose.override.yml").expanduser().as_posix(),
            #     ],
            # },
        ],
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            # "env_10_2": MetadataValue.json(env_10_2),
        },
    )


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
            "env_10_2": MetadataValue.json(env_10_2),
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
            "env_10_2": MetadataValue.json(env_10_2),
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
                "networks": [
                    "repository",
                ],
                "ports": [
                    f"{env_10_2.get('FILEBROWSER_PORT_HOST')}:{env_10_2.get('FILEBROWSER_PORT_CONTAINER')}",
                ],
                "volumes": [
                    f"{env_10_2.get('FILEBROWSER_DB')}:/filebrowser.db",
                    f"{env_10_2.get('FILEBROWSER_JSON')}:/.filebrowser.json",
                    f"{env_10_2.get('MONGO_DB_DIR')}:/opt/Thinkbox/DeadlineDatabase10/mongo/data:ro",
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
            "env_10_2": MetadataValue.json(env_10_2),
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
                    f"{env_10_2.get('MONGO_DB_DIR')}:/opt/Thinkbox/DeadlineDatabase10/mongo/data",
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
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose",
    compute_kind="python",
    ins={
        "env_base": AssetIn(),
        "build_kitsu": AssetIn(),
    },
)
def compose_kitsu(
        context: AssetExecutionContext,
        env_base: dict,
        build_kitsu: str,
) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "kitsu": {
                "container_name": "kitsu",
                "hostname": "kitsu",
                "domainname": env_base.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_kitsu,
                "volumes": [
                    f"{env_base.get('KITSU_POSTGRESQL_CONF')}:/etc/postgresql/14/main/postgresql.conf:ro",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT')}",
                    f"{env_base.get('NFS_ENTRY_POINT')}:{env_base.get('NFS_ENTRY_POINT_LNS')}",
                ],
                "ports": [
                    f"{env_base.get('KITSU_PORT_HOST')}:{env_base.get('KITSU_PORT_CONTAINER')}",
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
            "dagster-dev": {
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
        "connection_ini_10_2": AssetIn(),
    },
)
def compose_repository_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_repository_image_10_2: str,
        connection_ini_10_2: pathlib.Path,
) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "repository-10-2": {
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
                    f"{env_10_2.get('NFS_REPOSITORY')}:/opt/Thinkbox/DeadlineRepository10",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
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
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
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
            "likec4-dev": {
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
        "connection_ini_10_2": AssetIn(),
        "deadline_ini_10_2": AssetIn(),
    },
)
def compose_rcs_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_generic_runner_image_10_2: str,
        connection_ini_10_2: pathlib.Path,
        deadline_ini_10_2: pathlib.Path,

) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "deadline-rcs-runner-10-2": {
                "container_name": "deadline-rcs-runner-10-2",
                "hostname": "deadline-rcs-runner-10-2",
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
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('NFS_REPOSITORY')}:/opt/Thinkbox/DeadlineRepository10",
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
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_generic_runner_image_10_2": AssetIn(),
        "deadline_ini_10_2": AssetIn(),
        "connection_ini_10_2": AssetIn(),
    },
)
def compose_pulse_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_generic_runner_image_10_2: str,
        deadline_ini_10_2: pathlib.Path,
        connection_ini_10_2: pathlib.Path,

) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "deadline-pulse-runner-10-2": {
                "container_name": "deadline-pulse-runner-10-2",
                "hostname": "deadline-pulse-runner-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_generic_runner_image_10_2,
                "depends_on": {
                    "deadline-rcs-runner-10-2": {
                        "condition": "service_started",
                    },
                },
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": [
                    "--executable", "/opt/Thinkbox/Deadline10/bin/deadlinepulse",
                    "--nogui",
                    "--nosplash",
                ],
                "volumes": [
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('NFS_REPOSITORY')}:/opt/Thinkbox/DeadlineRepository10",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
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
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_generic_runner_image_10_2": AssetIn(),
        "deadline_ini_10_2": AssetIn(),
        "connection_ini_10_2": AssetIn(),
    },
)
def compose_worker_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_generic_runner_image_10_2: str,
        deadline_ini_10_2: pathlib.Path,
        connection_ini_10_2: pathlib.Path,

) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "deadline-worker-runner-10-2": {
                "container_name": "deadline-worker-runner-10-2",
                "hostname": "deadline-worker-runner-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_generic_runner_image_10_2,
                "depends_on": {
                    "deadline-rcs-runner-10-2": {
                        "condition": "service_started",
                    },
                },
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": [
                    "--executable", "/opt/Thinkbox/Deadline10/bin/deadlineworker",
                    "--nogui",
                    "--nosplash",
                ],
                "volumes": [
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('NFS_REPOSITORY')}:/opt/Thinkbox/DeadlineRepository10",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
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
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "build_generic_runner_image_10_2": AssetIn(),
        "deadline_ini_10_2": AssetIn(),
        "connection_ini_10_2": AssetIn(),
    },
)
def compose_webservice_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_generic_runner_image_10_2: str,
        deadline_ini_10_2: pathlib.Path,
        connection_ini_10_2: pathlib.Path,

) -> dict:
    """
    """

    docker_dict = {
        "services": {
            "deadline-webservice-runner-10-2": {
                "container_name": "deadline-webservice-runner-10-2",
                "hostname": "deadline-webservice-runner-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build_generic_runner_image_10_2,
                "depends_on": {
                    "deadline-rcs-runner-10-2": {
                        "condition": "service_started",
                    },
                },
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": [
                    "--executable", "/opt/Thinkbox/Deadline10/bin/deadlinewebservice",
                ],
                "volumes": [
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('NFS_REPOSITORY')}:/opt/Thinkbox/DeadlineRepository10",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
                ],
                "ports": [
                    f"{env_10_2.get('WEBSERVICE_HTTP_PORT_HOST')}:{env_10_2.get('WEBSERVICE_HTTP_PORT_CONTAINER')}",
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
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    group_name="Docker_Compose_10_2",
    compute_kind="python",
    ins={
        "env_10_2": AssetIn(),
        "compose_webservice_runner_10_2": AssetIn(),
        "compose_worker_runner_10_2": AssetIn(),
        "compose_pulse_runner_10_2": AssetIn(),
        "compose_rcs_runner_10_2": AssetIn(),
        # "compose_repository_10_2": AssetIn(),
        "compose_networks_10_2": AssetIn(),
        "compose_include_10_2": AssetIn(),
        "compose_mongo_express_10_2": AssetIn(),
        "compose_mongodb_10_2": AssetIn(),
        "compose_filebrowser_10_2": AssetIn(),
        "compose_dagster_dev": AssetIn(),
        "compose_likec4_dev": AssetIn(),
        "compose_kitsu": AssetIn(),
    },
)
def compose_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        compose_webservice_runner_10_2: dict,
        compose_worker_runner_10_2: dict,
        compose_pulse_runner_10_2: dict,
        compose_rcs_runner_10_2: dict,
        # compose_repository_10_2: dict,
        compose_networks_10_2: dict,
        compose_include_10_2: dict,
        compose_mongo_express_10_2: dict,
        compose_mongodb_10_2: dict,
        compose_filebrowser_10_2: dict,
        compose_dagster_dev: dict,
        compose_likec4_dev: dict,
        compose_kitsu: dict,
) -> pathlib.Path:
    """
    """

    docker_chainmap = ChainMap(
        compose_kitsu,
        compose_likec4_dev,
        compose_dagster_dev,
        compose_mongodb_10_2,
        compose_filebrowser_10_2,
        compose_mongo_express_10_2,
        compose_rcs_runner_10_2,
        compose_pulse_runner_10_2,
        compose_worker_runner_10_2,
        compose_webservice_runner_10_2,
        # compose_repository_10_2,
        compose_include_10_2,
        compose_networks_10_2,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)
    docker_yaml = yaml.dump(docker_dict)

    docker_compose = pathlib.Path(
        f"/home/michael/git/repos/deadline-docker/10.2/.docker/docker_compose/"
        f"{context.asset_key.path[0]}/docker-compose.yaml",
    )
    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    cmd_docker_compose_up = (f"/usr/bin/docker compose -f {docker_compose} -p {context.asset_key.path[0]} up "
                             f"--remove-orphans")
    cmd_docker_compose_down = (f"/usr/bin/docker compose -f {docker_compose} -p {context.asset_key.path[0]} down "
                               f"--remove-orphans")

    yield Output(docker_compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            # context.asset_key.path[0]: MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            context.asset_key.path[0]: MetadataValue.path(docker_compose),
            "cmd_docker_compose_up": MetadataValue.path(cmd_docker_compose_up),
            # "cmd_docker_compose_down": MetadataValue.path(cmd_docker_compose_down),
            "maps": MetadataValue.md(f"```json\n{json.dumps(docker_chainmap.maps, indent=2)}\n```"),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
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
) -> pydot.Dot:
    """
    """

    dcg = DockerComposeGraph()
    trees = dcg.parse_docker_compose(
        pathlib.Path(compose_10_2)
    )

    context.log.info(trees)

    dcg.iterate_trees(trees)

    dcg.graph.write(
        path=compose_10_2.parent / f"{context.asset_key.path[0]}.png",
        format="png",
    )

    dcg.graph.write(
        path=compose_10_2.parent / f"{context.asset_key.path[0]}.dot",
        format="dot",
    )

    # self.graph.write(
    #     path=pathlib.Path(__file__).parent.parent.parent / "tests" / "fixtures" / "out" / "main_graph.dot",
    #     format="dot",
    # )

    yield Output(dcg.graph)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(str(dcg.graph)),
            "dot": MetadataValue.path(compose_10_2.parent / f"{context.asset_key.path[0]}.dot"),
            "png": MetadataValue.path(compose_10_2.parent / f"{context.asset_key.path[0]}.png"),
        },
    )
