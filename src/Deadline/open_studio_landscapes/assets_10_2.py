import json
import tempfile
import urllib.parse
import shlex
import shutil
import textwrap
import pathlib
import time
import yaml
import subprocess
from collections import ChainMap
from functools import reduce

from python_on_whales import docker
from docker_graph.utils import *

from Deadline.open_studio_landscapes.constants import *
from Deadline.open_studio_landscapes.utils import *

from dagster import (
    AssetExecutionContext,
    asset,
    Output,
    AssetMaterialization,
    MetadataValue,
    AssetIn,
    AssetKey,
)


# Requirements:
# - [ ] ERROR: failed to solve: dockerfile parse error on line 4: invalid name for build stage: "10_2__build_base_image_10_2", name can't start with a number or contain symbols
# GROUP = ""
KEY = "Deadline_10_2"

asset_header = {
    # "group_name": GROUP,
    "key_prefix": [KEY],
    "compute_kind": "python"
}


# Todo
#  - [ ] Dockerfiles and docker_compose files to *context.asset_key.path,


@asset(
    **asset_header,
    group_name="Environment_10_2",
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

        f"DEADLINE_CLIENT_DEADLINE_INI_{KEY}": pathlib.Path(
            env_base["DOT_LANDSCAPES"],
            env_base.get("LANDSCAPE", "default"),
            KEY,
            "configs",
            "Deadline10",
            "deadline.ini",
        ).expanduser().as_posix(),

        f"DEADLINE_REPOSITORY_CONNECTION_INI_{KEY}": pathlib.Path(
            env_base["DOT_LANDSCAPES"],
            env_base.get("LANDSCAPE", "default"),
            KEY,
            "configs",
            "DeadlineRepository10",
            "settings",
            "connection.ini",
        ).expanduser().as_posix(),

        f"GOOGLE_ID_AWSPortalLink_{KEY}": "1VOQa6OyYUZj_7VILcD6EVl7YOfYVlCrU",
        f"GOOGLE_ID_DeadlineClient_{KEY}": "1cGxCPkrJ1ujWqie2yXTrOpShkEgSXR0F",
        f"GOOGLE_ID_DeadlineRepository_{KEY}": "1VZhCcxvCAc4oozLAKRCv_zwQLMuVdMRz",

        f"INSTALLER_AWSPortalLink_{KEY}": pathlib.Path(
            env_base["DOT_INSTALLERS"],
            KEY,
            "deadline",
            "deadline_10-2-1-1",
            "AWSPortalLink-1.2.1.0-linux-x64-installer.run",
            ).as_posix(),
        f"INSTALLER_DeadlineClient_{KEY}": pathlib.Path(
            env_base["DOT_INSTALLERS"],
            KEY,
            "deadline",
            "deadline_10-2-1-1",
            "DeadlineClient-10.2.1.1-linux-x64-installer.run",
            ).as_posix(),
        f"INSTALLER_DeadlineRepository_{KEY}": pathlib.Path(
            env_base["DOT_INSTALLERS"],
            KEY,
            "deadline",
            "deadline_10-2-1-1",
            "DeadlineRepository-10.2.1.1-linux-x64-installer.run",
            ).as_posix(),

        # This is where DeadlineRepository10 will get installed to:
        f"REPOSITORY_INSTALL_DESTINATION_{KEY}": pathlib.Path(
            env_base["DOT_LANDSCAPES"],
            env_base.get("LANDSCAPE", "default"),
            "__".join(context.asset_key.path),
            "data",
            "opt",
            "Thinkbox",
            "DeadlineRepository10",
            ).as_posix(),

        # This is where DeadlineDatabase10 will get installed to:
        # (provided MONGODB_INSIDE_CONTAINER is set to False)
        #
        # The Python script that comes with the mongodb docker image
        # initializes a DB if none is found at installation time.
        # That means, if DATABASE_INSTALL_DESTINATION_{KEY}
        # already points to an existing DB, this one will be used.
        # Make sure that the DB path has ownership of 101:65534.
        # Default would be inside a Landscape:
        # f"DATABASE_INSTALL_DESTINATION_{KEY}": pathlib.Path(
        #         DOT_DOCKER_ROOT,
        #         env_base.get("LANDSCAPE", "default"),
        #         "__".join(context.asset_key.path),
        #         "opt",
        #         "Thinkbox",
        #         "DeadlineDatabase10",
        #     ).as_posix(),
        f"DATABASE_INSTALL_DESTINATION_{KEY}": {
            #################################################################
            # Inside Landscape:
            "default": pathlib.Path(
                env_base["DOT_LANDSCAPES"],
                env_base.get("LANDSCAPE", "default"),
                "__".join(context.asset_key.path),
                "data",
                "opt",
                "Thinkbox",
                "DeadlineDatabase10",
            ).as_posix(),
            #################################################################
            # Test DB:
            "test_db_10_2": pathlib.Path(
                env_base["GIT_ROOT"],
                "tests",
                "fixtures",
                "__".join(context.asset_key.path),
                "DeadlineDatabase10",
            ).as_posix(),
        }["default"],
    }
    # @formatter:on

    env_base.update(_env)

    env_json = pathlib.Path(
        env_base["DOT_LANDSCAPES"],
        env_base.get("LANDSCAPE", "default"),
        "__".join(context.asset_key.path),
        f"{'__'.join(context.asset_key.path)}.json",
    )

    env_json.parent.mkdir(parents=True, exist_ok=True)

    with open(env_json, "w") as fw:
        json.dump(
            obj=env_base.copy(),
            fp=fw,
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )

    yield Output(env_base)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_base),
            "update": MetadataValue.json(_env),
            "json": MetadataValue.path(env_json),
        },
    )


@asset(
    **asset_header,
    group_name="Settings_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def connection_ini_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> pathlib.Path:
    # @formatter:off
    connection_ini = textwrap.dedent("""
    # {auto_generated}
    # {dagster_url}
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
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}", safe=":/%"),
        **env_10_2,
    )
    # @formatter:on

    deadline_connection_ini = pathlib.Path(env_10_2.get(f"DEADLINE_REPOSITORY_CONNECTION_INI_{KEY}"))

    deadline_connection_ini.parent.mkdir(parents=True, exist_ok=True)

    with open(deadline_connection_ini, "w") as fw:
        fw.write(connection_ini)

    yield Output(deadline_connection_ini)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(deadline_connection_ini),
            "connection_ini": MetadataValue.md(f"```\n{connection_ini}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Settings_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def deadline_ini_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> pathlib.Path:
    # @formatter:off
    deadline_ini = textwrap.dedent("""
    # {auto_generated}
    # {dagster_url}
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
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}", safe=":/%"),
        **env_10_2,
    )
    # @formatter:on

    deadline_client_ini = pathlib.Path(env_10_2.get(f"DEADLINE_CLIENT_DEADLINE_INI_{KEY}"))

    deadline_client_ini.parent.mkdir(parents=True, exist_ok=True)

    with open(deadline_client_ini, "w") as fw:
        fw.write(deadline_ini)

    yield Output(deadline_client_ini)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(deadline_client_ini),
            "connection_ini": MetadataValue.md(f"```\n{deadline_ini}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Build_Images_10_2",
)
def pip_packages_base_image_10_2(
        context: AssetExecutionContext,
) -> list:
    """
    """

    pip_packages: list = [
        # Todo:
        #  - [ ] (LOW) Deadline SSL authentication
        # "git+https://github.com/michimussato/SSLGeneration.git@packaging",
    ]

    yield Output(pip_packages)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(pip_packages),
        },
    )


@asset(
    **asset_header,
    group_name="Build_Images_10_2",
)
def wget_deadline_packages_base_image_10_2(
        context: AssetExecutionContext,
) -> dict[str, str]:
    """
    """

    ret: dict[str, str] = dict()

    ret["AWSPortalLink.run"] = "https://www.googleapis.com/drive/v3/files/{GOOGLE_ID_AWSPortalLink_10_2}?alt=media&key={SECRET_GOOGLE_API_KEY}"
    ret["DeadlineClient.run"] = "https://www.googleapis.com/drive/v3/files/{GOOGLE_ID_DeadlineClient_10_2}?alt=media&key={SECRET_GOOGLE_API_KEY}"
    ret["DeadlineRepository.run"] = "https://www.googleapis.com/drive/v3/files/{GOOGLE_ID_DeadlineRepository_10_2}?alt=media&key={SECRET_GOOGLE_API_KEY}"

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
        },
    )


if BUILD_FROM_GOOGLE_DRIVE_10_2:
    @asset(
        **asset_header,
        group_name="Build_Images_10_2",
        ins={
            "env_10_2": AssetIn(
                key_prefix=[KEY],
            ),
            "build_base_image": AssetIn(),
            "wget_deadline_packages_base_image_10_2": AssetIn(
                key_prefix=[KEY],
            ),
            "pip_packages_base_image_10_2": AssetIn(
                key_prefix=[KEY],
            ),
        },
    )
    def build_base_image_10_2(
            context: AssetExecutionContext,
            env_10_2: dict,
            build_base_image: str,
            wget_deadline_packages_base_image_10_2: dict[str, str],
            pip_packages_base_image_10_2: list,
    ) -> str:
        """
        """

        docker_file = pathlib.Path(
            env_10_2["DOT_LANDSCAPES"],
            env_10_2.get("LANDSCAPE"),
            # "__".join(context.asset_key.path),
            "Dockerfiles",
            "__".join(context.asset_key.path),
            "Dockerfile",
        )

        shutil.rmtree(docker_file.parent, ignore_errors=True)

        docker_file.parent.mkdir(parents=True, exist_ok=True)

        tags = [
            f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:latest",
            f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:{env_10_2.get('LANDSCAPE', str(time.time()))}",
        ]

        wget_str: str = get_wget_str(
            wget_packages=wget_deadline_packages_base_image_10_2
        )

        pip_install_str: str = get_pip_install_str(
            pip_install_packages=pip_packages_base_image_10_2
        )

        # @formatter:off
        docker_file_str = textwrap.dedent("""
            # {auto_generated}
            # {dagster_url}
            FROM {parent_image} AS {image_name}
            LABEL authors="{AUTHOR}"
            
            SHELL ["/bin/bash", "-c"]
            
            RUN apt-get update && apt-get upgrade -y
            
            {pip_install_str}
            
            WORKDIR /installers
            
            {wget_str}
            
            # Todo:
            # RUN thinkbox-ssl-gen --help
            
            RUN apt-get clean
            
            ENTRYPOINT []
        """).format(
            wget_str=wget_str.format(
                **env_10_2,
            ),
            pip_install_str=pip_install_str.format(
                **env_10_2,
            ),
            auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
            dagster_url=urllib.parse.quote(f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}", safe=":/%"),
            image_name="__".join(context.asset_key.path).lower(),
            parent_image=build_base_image,
            **env_10_2,
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
        )

        yield Output(tags[1])

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.path(tags[1]),
                "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
                **cmds_docker,
                "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
                "env_10_2": MetadataValue.json(env_10_2),
            },
        )

else:
    @asset(
        **asset_header,
        group_name="Build_Images_10_2",
        ins={
            "env_10_2": AssetIn(
                key_prefix=[KEY],
            ),
            "build_base_image": AssetIn(),
            "pip_packages_base_image_10_2": AssetIn(
                key_prefix=[KEY],
            ),
        },
    )
    def build_base_image_10_2(
            context: AssetExecutionContext,
            env_10_2: dict,
            build_base_image: str,
            pip_packages_base_image_10_2: list,
    ) -> str:
        """
        """

        docker_file = pathlib.Path(
            env_10_2["DOT_LANDSCAPES"],
            env_10_2.get("LANDSCAPE"),
            # KEY,
            "Dockerfiles",
            "__".join(context.asset_key.path),
            "Dockerfile",
        )

        shutil.rmtree(docker_file.parent, ignore_errors=True)

        docker_file.parent.mkdir(parents=True, exist_ok=True)

        # @formatter:off
        files_10_2 = {
            "AWSPortalLink.run": env_10_2.get(f"INSTALLER_AWSPortalLink_{KEY}"),
            "DeadlineClient.run": env_10_2.get(f"INSTALLER_DeadlineClient_{KEY}"),
            "DeadlineRepository.run": env_10_2.get(f"INSTALLER_DeadlineRepository_{KEY}"),
        }
        # @formatter:on

        tags = [
            f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:latest",
            f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:{env_10_2.get('LANDSCAPE', str(time.time()))}",
        ]

        pip_install_str: str = get_pip_install_str(
            pip_install_packages=pip_packages_base_image_10_2
        )

        with tempfile.TemporaryDirectory(
            dir=docker_file.parent,
            prefix="installer__",
        ) as tmpdir:

            copy_str: str = get_copy_str(
                temp_dir=tmpdir,
                copy_packages=files_10_2,
                mode=755,
            )

            # @formatter:off
            docker_file_str = textwrap.dedent("""
                # {auto_generated}
                # {dagster_url}
                FROM {parent_image} AS {image_name}
                LABEL authors="{AUTHOR}"
                
                SHELL ["/bin/bash", "-c"]
                
                RUN apt-get update && apt-get upgrade -y
                
                {pip_install_str}
                
                WORKDIR /installers
                
                {copy_str}
                
                # Todo:
                # RUN thinkbox-ssl-gen --help
                
                RUN apt-get clean
                
                ENTRYPOINT []
            """).format(
                copy_str=copy_str,
                pip_install_str=pip_install_str.format(
                    **env_10_2,
                ),
                auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
                dagster_url=urllib.parse.quote(f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}", safe=":/%"),
                image_name="__".join(context.asset_key.path).lower(),
                parent_image=build_base_image,
                **env_10_2,
            )
            # @formatter:on

            with open(docker_file, "w") as fw:
                fw.write(docker_file_str)

            with open(docker_file, "r") as fr:
                docker_file_content = fr.read()

            for key, value in files_10_2.items():
                shutil.copyfile(
                    src=value,
                    dst=pathlib.Path(tmpdir) / key,
                )

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
        )

        yield Output(tags[1])

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.path(tags[1]),
                "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
                **cmds_docker,
                "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
                "env_10_2": MetadataValue.json(env_10_2),
            },
        )


@asset(
    **asset_header,
    group_name="Repository_Installer_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
    description="This executes the Deadline Repository Installer. "
                "Needs to be done only once."
)
def deadline_command_install_repository_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> list:
    """
    """

    deadline_command = [
        "/installers/DeadlineRepository.run",
        "--mode", "unattended",
        "--prefix", "/opt/Thinkbox/DeadlineRepository10",
        "--setpermissions", "true",
        "--dbtype", "MongoDB",
        "--installmongodb", "false",
        "--dbhost", env_10_2.get("MONGO_DB_HOST"),
        "--dbport", env_10_2.get("MONGO_DB_PORT_HOST"),
        "--dbname", env_10_2.get("MONGO_DB_NAME"),
        "--dbauth", "false",
        "--dbssl", "false",
        "--installSecretsManagement", "false",
        "--importrepositorysettings", "false",
    ]

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
            "deadline_command": MetadataValue.path(" ".join(shlex.quote(s) for s in deadline_command)),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Repository_Installer_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "build_base_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
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
        env_10_2["DOT_LANDSCAPES"],
        env_10_2.get("LANDSCAPE", "default"),
        KEY,
        "Dockerfiles",
        "__".join(context.asset_key.path),
        "Dockerfile",
    )

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    tags = [
        f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:latest",
        f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:{env_10_2.get('LANDSCAPE', str(time.time()))}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # {auto_generated}
        # {dagster_url}
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        SHELL ["/bin/bash", "-c"]
        
        WORKDIR /installers
        
        ENTRYPOINT []
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}", safe=":/%"),
        image_name="__".join(context.asset_key.path).lower(),
        parent_image=build_base_image_10_2,
        **env_10_2,
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Repository_Installer_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_networks_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "build_repository_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_mongodb_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_command_install_repository_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
    description="This executes the Deadline Repository Installer. "
                "Needs to be done only once."
)
def compose_repository_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        compose_networks_10_2: dict,
        build_repository_image_10_2: str,
        compose_mongodb_10_2: dict,
        deadline_command_install_repository_10_2: list,
) -> pathlib.Path:
    """
    """

    docker_dict = {
        "services": {
            "repository-10-2": {
                "container_name": "repository-10-2",
                "hostname": "repository-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "networks": list(compose_networks_10_2.get("networks", {}).keys()),
                "depends_on": list(compose_mongodb_10_2.get("services", {}).keys()),
                "restart": "no",
                "image": build_repository_image_10_2,
                "command": deadline_command_install_repository_10_2,
                "volumes": [
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
                    f"{env_10_2.get('REPOSITORY_INSTALL_DESTINATION_10_2')}:/opt/Thinkbox/DeadlineRepository10",
                ],
            },
        },
    }

    docker_chainmap = ChainMap(
        compose_networks_10_2,
        compose_mongodb_10_2,
        docker_dict,
    )

    docker_chainmap_dict = reduce(deep_merge, docker_chainmap.maps)

    docker_yaml = yaml.dump(docker_chainmap_dict)

    docker_compose = pathlib.Path(
        env_10_2["DOT_LANDSCAPES"],
        env_10_2.get("LANDSCAPE", "default"),
        "docker_compose",
        *context.asset_key.path,
        "docker-compose.yml",
    )
    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    project_name = f"{'__'.join(context.asset_key.path)}__{env_10_2.get('LANDSCAPE', 'default').replace('.', '-')}"

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "up",
        "--remove-orphans",
        "--abort-on-container-exit",
    ]

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "down",
        "--remove-orphans",
    ]

    yield Output(docker_compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "cmd_docker_compose_up": MetadataValue.path(" ".join(shlex.quote(s) for s in cmd_docker_compose_up)),
            "cmd_docker_compose_down": MetadataValue.path(" ".join(shlex.quote(s) for s in cmd_docker_compose_down)),
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Build_Images_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
    description=""
)
def deadline_command_build_client_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> list:
    """
    """

    deadline_command = [
        "/installers/DeadlineClient.run",
        "--mode", "unattended",
        "--prefix", "/opt/Thinkbox/Deadline10",
        "--setpermissionsclient", "true",
        # "--binariesonly", "true",
        "--repositorydir", "/opt/Thinkbox/DeadlineRepository10",
        "--launcherdaemon", "false",
        "--httpport", env_10_2.get("RCS_HTTP_PORT_CONTAINER"),
        "--enabletls", "false",
        "--proxyalwaysrunning", "false",
        "--blockautoupdateoverride", "NotBlocked",
        "--webserviceuser", "root",
        "--webservice_httpport", env_10_2.get("WEBSERVICE_HTTP_PORT_CONTAINER"),
        "--webservice_enabletls", "false",
        # This is new for 10.4:
        # "--remotecontrol", "NotBlocked",
    ]

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
            "deadline_command": MetadataValue.path(" ".join(shlex.quote(s) for s in deadline_command)),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Build_Images_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "build_base_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_command_build_client_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def build_client_image_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_base_image_10_2: str,
        deadline_command_build_client_image_10_2: list,
) -> str:
    """
    """

    docker_file = pathlib.Path(
        env_10_2["DOT_LANDSCAPES"],
        env_10_2.get("LANDSCAPE", "default"),
        KEY,
        "Dockerfiles",
        "__".join(context.asset_key.path),
        "Dockerfile",
    )

    tags = [
        f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:latest",
        f"{env_10_2.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:{env_10_2.get('LANDSCAPE', str(time.time()))}",
    ]

    # @formatter:off
    docker_file_str = textwrap.dedent("""
        # {auto_generated}
        # {dagster_url}
        FROM {parent_image} AS {image_name}
        LABEL authors="{AUTHOR}"
        
        SHELL ["/bin/bash", "-c"]
        
        WORKDIR /installers
        
        RUN {deadline_command}
        
        WORKDIR /opt/Thinkbox
        
        ENTRYPOINT []
    """).format(
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}", safe=":/%"),
        image_name="__".join(context.asset_key.path).lower(),
        parent_image=build_base_image_10_2,
        deadline_command=" ".join(shlex.quote(s) for s in deadline_command_build_client_image_10_2),
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
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "compose_override_ayon": AssetIn(
            AssetKey(["Ayon", "compose_override"]),
        ),
    },
)
def compose_include_10_2(
        context: AssetExecutionContext,
        compose_override_ayon: dict,
) -> dict:
    docker_dict = {
        "include": [
            compose_override_ayon,
        ],
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
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
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
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
                #Todo
                # "healthcheck": {
                #     "test": ["CMD", "wget", "-S", f"http://0.0.0.0:{env_10_2.get('MONGO_EXPRESS_PORT_CONTAINER')}"],
                #     "interval": "10s",
                #     "timeout": "2s",
                #     "retries": "3",
                # },
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
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def compose_filebrowser_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> dict:

    image = "filebrowser/filebrowser"

    volumes = [
        f"{env_10_2.get('FILEBROWSER_DB')}:/filebrowser.db",
        f"{env_10_2.get('FILEBROWSER_JSON')}:/.filebrowser.json",
        f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}:ro",
        f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}:ro",
    ]

    docker_dict = {
        "services": {
            "filebrowser": {
                "image": image,
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
                "volumes": volumes,
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def script_chown_mongodb_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> dict[str, str]:

    ret = dict()

    ret["exe"] = shutil.which("bash")
    ret["script"] = str()

    mongo_db_dir_host = pathlib.Path(
        env_10_2.get(f"DATABASE_INSTALL_DESTINATION_{KEY}")
    )

    # sudo chown 101:65534 DeadlineDatabase10
    # Concept: /usr/bin/sshpass -eENV_VAR /usr/bin/ssh "echo $ENV_VAR | sudo -S <cmd>"
    # Because shutil.chown cannot sudo

    mongo_uid = 101
    mongo_gid = 65534

    # @formatter:off
    ret["script"] += "#!/bin/bash\n"
    ret["script"] += "\n"
    # ret["script"] += f"{shutil.which('sshpass')} -eSSH_PASS ssh {env_10_2['SSH_USER']}@{env_10_2['SSH_HOST']} \"echo $SSH_PASS | sudo -S chown {mongo_uid}:{mongo_gid} {mongo_db_dir_host.as_posix()}\"\n"
    ret["script"] += f"echo $SUDO_PASS | sudo -S -k /usr/bin/chown {mongo_uid}:{mongo_gid} {mongo_db_dir_host.as_posix()};\n"
    ret["script"] += "\n"
    ret["script"] += "echo Success;\n"
    ret["script"] += "exit 0;\n"
    # @formatter:on

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
            "script_chown": MetadataValue.md(f"```shell\n{ret['script']}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "script_chown_mongodb_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def compose_mongodb_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        script_chown_mongodb_10_2: dict[str, str],
) -> dict:

    image = "mongodb/mongodb-community-server:4.4-ubuntu2004"

    cmd_docker_run = [
        shutil.which("docker"),
        "run",
        "--rm",
        "--interactive",
        "--tty",
        image,
        "/bin/bash",
    ]

    volumes = [
        f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}:ro",
        f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}:ro",
    ]

    mongo_db_dir_host = pathlib.Path(env_10_2.get(f"DATABASE_INSTALL_DESTINATION_{KEY}"))
    mongo_db_dir_host.mkdir(parents=True, exist_ok=True)

    stdout_stderr = {
        "stdout": MetadataValue.md(f"```shell\nNone\n```"),
        "stderr": MetadataValue.md(f"```shell\nNone\n```"),
    }

    if not MONGODB_INSIDE_CONTAINER:

        if bool(script_chown_mongodb_10_2["script"]):

            context.log.info(f"Setting ownership of {mongo_db_dir_host.as_posix()}...")

            proc = subprocess.Popen(
                script_chown_mongodb_10_2["exe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                env={
                    "SUDO_PASS": env_10_2['SUDO_PASS'],
                }
            )

            stdout, stderr = proc.communicate(
                input=script_chown_mongodb_10_2["script"].encode(),
            )

            stdout_stderr = {
                "stdout": MetadataValue.md(f"```shell\n{stdout.decode(encoding='utf-8')}\n```"),
                "stderr": MetadataValue.md(f"```shell\n{stderr.decode(encoding='utf-8')}\n```"),
            }

            # helpers.iterate_fds(
            #     (
            #         proc.stderr,
            #         proc.stdout,
            #     ),
            #     (
            #         context.log.warning,
            #         context.log.info,
            #     )
            # )

        volumes.insert(
            0,
            f"{mongo_db_dir_host.as_posix()}:{env_10_2.get('DEFAULT_DBPATH_CONTAINER')}",
        )

    docker_dict = {
        "services": {
            "mongodb-10-2": {
                "image": image,
                "container_name": "mongodb-10-2",
                "hostname": "mongodb-10-2",
                "domainname": env_10_2.get("ROOT_DOMAIN"),
                "restart": "always",
                "command": [
                    "--port", env_10_2.get("MONGO_DB_PORT_CONTAINER"),
                    "--dbpath", f"{env_10_2.get('DEFAULT_DBPATH_CONTAINER')}",
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
                "volumes": volumes,
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```shell\n{docker_yaml}\n```"),
            "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
            **stdout_stderr,
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
    description="This executes the Deadline Repository Installer. "
                "Needs to be done only once."
)
def deadline_command_compose_rcs_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> list:
    """
    """

    deadline_command = [
        "/opt/Thinkbox/Deadline10/bin/deadlinercs",
    ]

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
            "deadline_command": MetadataValue.path(" ".join(shlex.quote(s) for s in deadline_command)),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "build_client_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "connection_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_command_compose_rcs_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def compose_rcs_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_client_image_10_2: str,
        connection_ini_10_2: pathlib.Path,
        deadline_ini_10_2: pathlib.Path,
        deadline_command_compose_rcs_runner_10_2: list,

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
                "image": build_client_image_10_2,
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": deadline_command_compose_rcs_runner_10_2,
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", f"http://localhost:{env_10_2.get('RCS_HTTP_PORT_CONTAINER')}"],
                    "interval": "10s",
                    "timeout": "2s",
                    "retries": "3",
                },
                "volumes": [
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('REPOSITORY_INSTALL_DESTINATION_10_2')}:/opt/Thinkbox/DeadlineRepository10",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT')}",
                    f"{env_10_2.get('NFS_ENTRY_POINT')}:{env_10_2.get('NFS_ENTRY_POINT_LNS')}",
                ],
                "ports": [
                    f"{env_10_2.get('RCS_HTTP_PORT_HOST')}:{env_10_2.get('RCS_HTTP_PORT_CONTAINER')}",
                    #Todo:
                    # - [ ] Expose Deadline standard Ports (https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/manual/considerations.html#firewall-anti-virus-security-considerations)
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
    description="This executes the Deadline Repository Installer. "
                "Needs to be done only once."
)
def deadline_command_compose_pulse_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> list:
    """
    """

    deadline_command = [
        "/opt/Thinkbox/Deadline10/bin/deadlinepulse",
        "-nogui",
        "-nosplash",
    ]

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
            "deadline_command": MetadataValue.path(" ".join(shlex.quote(s) for s in deadline_command)),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "build_client_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "connection_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_command_compose_pulse_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def compose_pulse_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_client_image_10_2: str,
        deadline_ini_10_2: pathlib.Path,
        connection_ini_10_2: pathlib.Path,
        deadline_command_compose_pulse_runner_10_2: list,

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
                "image": build_client_image_10_2,
                "depends_on": {
                    "deadline-rcs-runner-10-2": {
                        "condition": "service_started",
                    },
                },
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": deadline_command_compose_pulse_runner_10_2,
                "volumes": [
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('REPOSITORY_INSTALL_DESTINATION_10_2')}:/opt/Thinkbox/DeadlineRepository10",
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
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
    description="This executes the Deadline Repository Installer. "
                "Needs to be done only once."
)
def deadline_command_compose_worker_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> list:
    """
    """

    deadline_command = [
        "/opt/Thinkbox/Deadline10/bin/deadlineworker",
        "-nogui",
        "-nosplash",
    ]

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
            "deadline_command": MetadataValue.path(" ".join(shlex.quote(s) for s in deadline_command)),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "build_client_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "connection_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_command_compose_worker_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def compose_worker_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_client_image_10_2: str,
        deadline_ini_10_2: pathlib.Path,
        connection_ini_10_2: pathlib.Path,
        deadline_command_compose_worker_runner_10_2: list,

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
                "image": build_client_image_10_2,
                "depends_on": {
                    "deadline-rcs-runner-10-2": {
                        "condition": "service_started",
                    },
                },
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": deadline_command_compose_worker_runner_10_2,
                "volumes": [
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('REPOSITORY_INSTALL_DESTINATION_10_2')}:/opt/Thinkbox/DeadlineRepository10",
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
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
    description="This executes the Deadline Repository Installer. "
                "Needs to be done only once."
)
def deadline_command_compose_webservice_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
) -> list:
    """
    """

    deadline_command = [
        "/opt/Thinkbox/Deadline10/bin/deadlinewebservice",
    ]

    yield Output(deadline_command)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(deadline_command),
            "deadline_command": MetadataValue.path(" ".join(shlex.quote(s) for s in deadline_command)),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "build_client_image_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "connection_ini_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "deadline_command_compose_webservice_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
    },
)
def compose_webservice_runner_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        build_client_image_10_2: str,
        deadline_ini_10_2: pathlib.Path,
        connection_ini_10_2: pathlib.Path,
        deadline_command_compose_webservice_runner_10_2: list,

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
                "image": build_client_image_10_2,
                "depends_on": {
                    "deadline-rcs-runner-10-2": {
                        "condition": "service_started",
                    },
                },
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", f"http://localhost:{env_10_2.get('WEBSERVICE_HTTP_PORT_CONTAINER')}"],
                    "interval": "10s",
                    "timeout": "2s",
                    "retries": "3",
                },
                "networks": [
                    "repository",
                    "mongodb",
                ],
                "command": deadline_command_compose_webservice_runner_10_2,
                "volumes": [
                    f"{deadline_ini_10_2.as_posix()}:/var/lib/Thinkbox/Deadline10/deadline.ini:ro",
                    f"{connection_ini_10_2.as_posix()}:/opt/Thinkbox/DeadlineRepository10/settings/connection.ini:ro",
                    f"{env_10_2.get('REPOSITORY_INSTALL_DESTINATION_10_2')}:/opt/Thinkbox/DeadlineRepository10",
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
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_dict": MetadataValue.md(f"```json\n{json.dumps(docker_dict, indent=2)}\n```"),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )


@asset(
    **asset_header,
    group_name="Docker_Compose_10_2",
    ins={
        "env_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_webservice_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_worker_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_pulse_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_rcs_runner_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_networks_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_include_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_mongo_express_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_mongodb_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_filebrowser_10_2": AssetIn(
            key_prefix=[KEY],
        ),
        "compose_grafana": AssetIn(
            AssetKey(["Grafana", "compose"])),
        "compose_dagster": AssetIn(
            AssetKey(["Dagster", "compose"])),
        "compose_likec4": AssetIn(
            AssetKey(["LikeC4", "compose"])),
        "compose_kitsu": AssetIn(
            AssetKey(["Kitsu", "compose"])),
    },
)
def compose_10_2(
        context: AssetExecutionContext,
        env_10_2: dict,
        compose_webservice_runner_10_2: dict,
        compose_worker_runner_10_2: dict,
        compose_pulse_runner_10_2: dict,
        compose_rcs_runner_10_2: dict,
        compose_networks_10_2: dict,
        compose_include_10_2: dict,
        compose_mongo_express_10_2: dict,
        compose_mongodb_10_2: dict,
        compose_filebrowser_10_2: dict,
        compose_grafana: dict,
        compose_dagster: dict,
        compose_likec4: dict,
        compose_kitsu: dict,
) -> pathlib.Path:
    """
    """

    docker_chainmap = ChainMap(
        compose_kitsu,
        compose_likec4,
        compose_dagster,
        compose_grafana,
        compose_mongodb_10_2,
        compose_filebrowser_10_2,
        compose_mongo_express_10_2,
        compose_rcs_runner_10_2,
        compose_pulse_runner_10_2,
        compose_worker_runner_10_2,
        compose_webservice_runner_10_2,
        compose_include_10_2,
        compose_networks_10_2,
    )

    docker_dict = reduce(deep_merge, docker_chainmap.maps)
    docker_yaml = yaml.dump(docker_dict)

    docker_compose = pathlib.Path(
        env_10_2["DOT_LANDSCAPES"],
        env_10_2.get("LANDSCAPE", "default"),
        # KEY,
        "docker_compose",
        "__".join(context.asset_key.path),
        "docker-compose.yml",
    )

    docker_compose.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_compose, "w") as fw:
        fw.write(docker_yaml)

    project_name = f"{'__'.join(context.asset_key.path)}__{env_10_2.get('LANDSCAPE', 'default').replace('.', '-')}"

    cmd_docker_compose_up = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "up",
        "--remove-orphans",
    ]

    cmd_docker_compose_down = [
        shutil.which("docker"),
        "compose",
        "--file",
        docker_compose.as_posix(),
        "--project-name",
        project_name,
        "down",
        "--remove-orphans",
    ]

    yield Output(docker_compose)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "cmd_docker_compose_up": MetadataValue.path(" ".join(shlex.quote(s) for s in cmd_docker_compose_up)),
            "cmd_docker_compose_down": MetadataValue.path(" ".join(shlex.quote(s) for s in cmd_docker_compose_down)),
            "__".join(context.asset_key.path): MetadataValue.path(docker_compose),
            "maps": MetadataValue.md(f"```json\n{json.dumps(docker_chainmap.maps, indent=2)}\n```"),
            "yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "env_10_2": MetadataValue.json(env_10_2),
        },
    )
