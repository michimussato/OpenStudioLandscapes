import base64
import json
import pathlib
import shutil
import textwrap
import time
import urllib.parse
from typing import Dict, Generator

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
    multi_asset,
    AssetSpec, AssetOut,
)

from OpenStudioLandscapes.engine.config import dist
from OpenStudioLandscapes.engine.config.models import ConfigEngine, DockerConfigModel
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesBaseOut
from OpenStudioLandscapes.engine.policies.retry import build_docker_image_retry_policy
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.docker import *

# @asset(
#     **ASSET_HEADER_BASE,
# )
# def pip_packages(
#     context: AssetExecutionContext,
# ) -> Generator[Output[List] | AssetMaterialization, None, None]:
#     """ """
#
#     _pip_packages: list = [
#         # Content moved to OpenStudioLandscapes.Dagster.assets.pip_packages
#         # Todo:
#         #  - [ ] enable OpenStudioLandscapes after making it public
#         #  - [x] maybe move dagster stuff to dagster image?
#     ]
#
#     yield Output(_pip_packages)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(_pip_packages),
#         },
#     )


# @asset(
#     **ASSET_HEADER_BASE,
# )
# def apt_packages(
#     context: AssetExecutionContext,
# ) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
#     """ """
#
#     _apt_packages = {}
#
#     _apt_packages["base"] = [
#         "git",
#         "ca-certificates",
#         "htop",
#         "file",
#         "tzdata",
#         "curl",
#         "wget",
#         "ffmpeg",
#         "xvfb",
#         "libegl1",
#         "libsm6",
#         "libglu1-mesa",
#         "libxss1",
#     ]
#
#     _apt_packages["build_python311"] = [
#         "build-essential",
#         "pkg-config",
#         "zlib1g-dev",
#         "libncurses5-dev",
#         "libgdbm-dev",
#         "libnss3-dev",
#         "libssl-dev",
#         "libreadline-dev",
#         "libffi-dev",
#         "libsqlite3-dev",
#         "libbz2-dev",
#         "iproute2",
#         "liblzma-dev",
#     ]
#
#     yield Output(_apt_packages)
#
#     yield AssetMaterialization(
#         asset_key=context.asset_key,
#         metadata={
#             "__".join(context.asset_key.path): MetadataValue.json(_apt_packages),
#         },
#     )


@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "CONFIG": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])),
    },
)
def write_dockerfile(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    CONFIG: ConfigEngine,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:
    """ """

    docker_file = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{dist.name}",
        "__".join(context.asset_key.path),
        "Dockerfiles",
        "Dockerfile",
    )

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    image_name = get_image_name(context=context)
    context.log.debug(f"{image_name = }")

    docker_config: DockerConfigModel = CONFIG.openstudiolandscapes__docker_config

    image_prefixes = parse_docker_image_path(
        docker_config=docker_config,
        context=context,
    )
    context.log.debug(f"{image_prefixes = }")

    tags = [
        env.get("LANDSCAPE", str(time.time())),
    ]
    context.log.debug(f"{tags = }")

    apt_install_str_base: str = get_apt_install_str(
        apt_install_packages=[
            *CONFIG.apt_packages_base,
            *CONFIG.openstudiolandscapes__rez_config.apt_packages_rez,
        ],
    )

    apt_install_str_build_python311: str = get_apt_install_str(
        apt_install_packages=CONFIG.apt_packages_build_python311,
    )

    pip_install_str: str = get_pip_install_str(pip_install_packages=CONFIG.pip_packages)

    # Ubuntu -> minimal deb
    # - https://askubuntu.com/a/445496
    # - https://hub.docker.com/_/debian

    # @formatter:off
    docker_file_str = textwrap.dedent("""\
        # {auto_generated}
        # {dagster_url}
        
        ################################################################################
        # Multi Stage: Stage 1
        # 1.05GB
        # FROM docker.io/ubuntu:20.04 AS base
        # FROM docker.io/phusion/baseimage:focal-1.2.0 AS base  # 1.52GB
        # FROM docker.io/debian:bullseye AS base  # 1.34GB
        # 1GB
        FROM docker.io/debian:bullseye-slim AS base
        LABEL authors="{AUTHOR}"

        ARG DEBIAN_FRONTEND=noninteractive

        ENV CONTAINER_TIMEZONE={timezone}
        ENV SET_CONTAINER_TIMEZONE=true
            
        # Prepend to PATH /opt/python{PYTHON_MAJ}.{PYTHON_MIN}/bin
        ENV PATH="/opt/python{PYTHON_MAJ}.{PYTHON_MIN}/bin:$PATH"
        # Prepend to PATH /opt/rez/bin/rez
        ENV PATH="/opt/rez/bin/rez:$PATH"

        ENV LC_ALL=C.UTF-8
        ENV LANG=C.UTF-8

        SHELL ["/bin/bash", "-c"]

        # This would reduce storage
        # 1.26GB -> 1.25GB
        RUN apt-get update \\
            && apt-get upgrade -y \\
            && apt-get -y autoremove --purge \\
            && apt-get -y clean \\
            && apt-get autoclean

        {apt_install_str_base}
        
        ################################################################################
        # Multi Stage: Stage 2
        FROM base AS build_python

        {apt_install_str_build_python311}

        WORKDIR /build/python

        RUN curl "https://www.python.org/ftp/python/{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}/Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz" -o Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz \\
            && file Pytdocker_confighon-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz \\
            && tar -xvf Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz \\
            && rm --force Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}.tgz

        # altinstall instead of install because the later command will overwrite the default system python3 binary.
        RUN pushd Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT} \\
            && ./configure --enable-optimizations --prefix /opt/python{PYTHON_MAJ}.{PYTHON_MIN} \\
            && make -j $(nproc) \\
            && make altinstall \\
            && popd \\
            && rm -rf Python-{PYTHON_MAJ}.{PYTHON_MIN}.{PYTHON_PAT}

        WORKDIR /opt/python3.11/bin
        RUN ln -s python3.11 python
        
        ################################################################################
        # Multi Stage: Stage Rez
        # # Rez Installer
        FROM base AS rez_installer
        
        COPY --from=build_python "/opt/python{PYTHON_MAJ}.{PYTHON_MIN}" "/opt/python{PYTHON_MAJ}.{PYTHON_MIN}"

        WORKDIR /build/rez

        RUN curl -L "https://github.com/AcademySoftwareFoundation/rez/archive/refs/tags/{rez_version}.tar.gz" -o rez-{rez_version}.tar.gz \\
            && file rez-{rez_version}.tar.gz \\
            && tar -xzvf rez-{rez_version}.tar.gz \\
            && rm --force rez-{rez_version}.tar.gz

        RUN python3.11 ./rez-{rez_version}/install.py --verbose /opt/rez

        RUN chmod +x /opt/rez/completion/complete.sh
        RUN /opt/rez/completion/complete.sh
        
        # # Rez Build Test
        FROM rez_installer AS rez_build_test
        
        WORKDIR /build/rez/rez-{rez_version}/example_packages/hello_world

        RUN rez bind -vvvvv --quickstart
        RUN rez build -vvvvv --install

        RUN rez env -vvvvv hello_world -- hello > /rez_hello_world_test.txt

        ################################################################################        
        # Multi Stage: Stage FINAL
        FROM base AS {image_name}
        
        COPY --from=build_python "/opt/python{PYTHON_MAJ}.{PYTHON_MIN}" "/opt/python{PYTHON_MAJ}.{PYTHON_MIN}"
        COPY --from=rez_installer  "/opt/rez" "/opt/rez"
        COPY --from=rez_build_test "/rez_hello_world_test.txt" "/rez_hello_world_test.txt"

        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore --upgrade pip setuptools setuptools_scm wheel \\
            && python{PYTHON_MAJ}.{PYTHON_MIN} -m pip cache purge

        {pip_install_str}

        ENTRYPOINT []
        CMD []
        """).format(
        apt_install_str_base=apt_install_str_base,
        apt_install_str_build_python311=apt_install_str_build_python311,
        pip_install_str=pip_install_str.format(
            **env,
        ),
        rez_version=CONFIG.openstudiolandscapes__rez_config.rez_version,
        timezone=CONFIG.tz,
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(
            f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}",
            safe=":/%",
        ),
        image_name=image_name,
        **env,
    )
    # @formatter:on

    with open(docker_file, mode="w", encoding="utf-8") as fw:
        fw.write(docker_file_str)

    with open(docker_file, mode="r") as fr:
        docker_file_content = fr.read()

    yield Output(docker_file)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(docker_file),
            docker_file.name: MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "CONFIG": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])),
        "docker_config_json": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "docker_config_json"])
        ),
        "write_dockerfile": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "write_dockerfile"])
        ),
    },
    retry_policy=build_docker_image_retry_policy,
)
def build_docker_image(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    CONFIG: ConfigEngine,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
    write_dockerfile: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | list[str]]] | AssetMaterialization, None, None]:
    """ """

    image_name = get_image_name(context=context)
    context.log.debug(f"{image_name = }")

    docker_config: DockerConfigModel = CONFIG.openstudiolandscapes__docker_config

    image_prefixes = parse_docker_image_path(
        docker_config=docker_config,
        context=context,
    )
    context.log.debug(f"{image_prefixes = }")

    tags = [
        env.get("LANDSCAPE", str(time.time())),
    ]
    context.log.debug(f"{tags = }")

    image_data = {
        "image_name": image_name,
        "image_prefixes": image_prefixes,
        "image_tags": tags,
        "image_parent": {},
    }

    # just highlight the message
    context.log.debug(f"{image_data = }")

    # Full command as per python-on-whales
    # Build command (public) (OK: [x]):  /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json build --quiet --pull --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles/Dockerfile --no-cache --tag openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9 --tag harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9 /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles
    # Push command (public):             /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json image push harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9
    # Build command (private) (OK: [x]): /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json build --quiet --pull --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles/Dockerfile --no-cache --tag openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666 --tag harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666 /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles
    # Push command (private):            /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json image push harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666

    cmds = []

    # tags_local = [f"{image_prefix_local}{image_name}:{tag}" for tag in tags]
    tags_full_str = [f"{image_prefixes}{image_name}:{tag}" for tag in tags]
    context.log.debug(f"{tags_full_str = }")

    cmd_build = docker_build_cmd(
        context=context,
        docker_config_json=docker_config_json,
        docker_file=write_dockerfile,
        tags=tags_full_str,
        pull=docker_config.use_registry
        and docker_config.docker_registry_config.docker_pull,
        no_cache=docker_config.no_cache,
    )

    cmds.append(cmd_build)

    if (
        docker_config.use_registry and docker_config.docker_registry_config.docker_push
    ):  # or not_push
        cmds_push = docker_push_cmd(
            context=context,
            docker_config_json=docker_config_json,
            tags_full=tags_full_str,
        )

        cmds.extend(cmds_push)
    else:
        pass

    context.log.info(f"{cmds = }")
    # cmds = [['/usr/local/bin/docker', '--debug', '--config', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-11-16-17-38-11-6545bb6740ab406189bad0aa0820844f/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json', 'build', '--progress', 'plain', '--pull', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-11-16-17-38-11-6545bb6740ab406189bad0aa0820844f/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles/Dockerfile', '--no-cache', '--tag', 'openstudiolandscapes_base_build_docker_image:2025-11-16-17-38-11-6545bb6740ab406189bad0aa0820844f', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-11-16-17-38-11-6545bb6740ab406189bad0aa0820844f/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles'], ['/usr/local/bin/docker', '--config', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-11-16-17-38-11-6545bb6740ab406189bad0aa0820844f/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json', 'push', 'openstudiolandscapes_base_build_docker_image:2025-11-16-17-38-11-6545bb6740ab406189bad0aa0820844f']]

    logs = docker_do(
        context=context,
        cmds=cmds,
    )

    yield Output(image_data)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(image_data),
            "env": MetadataValue.json(env),
            "docker_image": MetadataValue.path(
                f"{image_data['image_prefixes']}{image_data['image_name']}:{image_data['image_tags'][0]}"
            ),
            "docker_cmd": MetadataValue.path(
                get_docker_run_cmd(
                    context=context,
                    image_data=image_data,
                )
            ),
            "logs": MetadataValue.json(logs),
        },
    )

group_out_base = AssetSpec(
    key=AssetKey(
        [
            *ASSET_HEADER_BASE["key_prefix"],
            "group_out_base",
        ]
    ),
    # deps=[
    #     AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"]),
    #     AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"]),
    #     AssetKey([*ASSET_HEADER_BASE["key_prefix"], "docker_config_json"]),
    #     AssetKey([*ASSET_HEADER_BASE["key_prefix"], "build_docker_image"]),
    # ],
    group_name=ASSET_HEADER_BASE["group_name"],
    description=textwrap.dedent("""
        This is the foundation. This assets provides all relevant environment information
        for subsequent assets and asset groups. All downstream assets consume this data and
        build their environment on top of this.
        """)
)
@multi_asset(
    # **ASSET_HEADER_BASE,
    outs={
        "group_out_base": AssetOut.from_spec(
            group_out_base,
        )
    },
    # Todo:
    #  - [ ] still necessary?
    # tags={
    #     "group_out": "base",
    # },
    # specs=[
    #     group_out_base,
    # ],
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "CONFIG": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])),
        "docker_config_json": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "docker_config_json"])
        ),
        "build_docker_image": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "build_docker_image"]),
        ),
    },
    # description=textwrap.dedent("""
    #     This is the foundation. This assets provides all relevant environment information
    #     for subsequent assets and asset groups. All downstream assets consume this data and
    #     build their environment on top of this.
    #     """),
)
def group_out_base(
    context: AssetExecutionContext,
    env: Dict,  # pylint: disable=redefined-outer-name
    CONFIG: ConfigEngine,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
    build_docker_image: Dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[OpenStudioLandscapesBaseOut] | AssetMaterialization, None, None]:

    group_out_base: OpenStudioLandscapesBaseOut = OpenStudioLandscapesBaseOut(
        env=env,
        config_engine=CONFIG,
        docker_config_json=docker_config_json,
        docker_image_base=build_docker_image,
    )

    context.log.debug(f"group_out_base {group_out_base = }")

    output_name = "group_out_base"

    yield Output(
        output_name=output_name,
        value=group_out_base,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output(output_name),
        metadata={
            "group_out_base": MetadataValue.md(
                f"```json\n{group_out_base.model_dump_json(indent=2, fallback=str)}\n```"
            ),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "CONFIG": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])),
    },
)
def docker_config_json(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    CONFIG: ConfigEngine,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    dockercfg_path = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{dist.name}",
        "__".join(context.asset_key.path),
        "config.json",
    )

    dockercfg_path.parent.mkdir(parents=True, exist_ok=True)

    docker_auth = {}
    docker_auth["auths"] = auths = {}

    docker_config: DockerConfigModel = CONFIG.openstudiolandscapes__docker_config

    # process from docker/api/config.py:create_config
    # (https://docker-py.readthedocs.io/en/stable/api.html#docker.api.config.ConfigApiMixin.create_config)
    username: str = docker_config.docker_registry_config.docker_registry_username
    password: str = docker_config.docker_registry_config.docker_registry_password
    fqdn: str = docker_config.docker_registry_config.docker_registry_fqdn
    protocol: str = docker_config.docker_registry_config.docker_registry_protocol
    port: int = docker_config.docker_registry_config.docker_registry_port
    url_: str = f"{protocol}://{fqdn}"

    credentials_str = f"{username}:{password}"
    credentials_bytes = credentials_str.encode("utf-8")
    credentials_encoded = base64.b64encode(credentials_bytes).decode("ascii")

    auths[f"{url_}:{port}"] = {"auth": credentials_encoded}

    # docker client does not pick up the dockercfg_path
    # if the file is not present
    with dockercfg_path.open(mode="w") as fo:
        json.dump(
            docker_auth,
            fo,
            indent="\t",
            sort_keys=True,
            separators=(",", ": "),
        )

    # The command to log in to the docker registry
    # using this config.json:
    # docker --config /dir/where/config_json/lives/ login http://harbor.farm.evil:80

    yield Output(dockercfg_path.parent)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(
                dockercfg_path.parent
            ),
            "config_json": MetadataValue.path(dockercfg_path),
            "docker_auth": MetadataValue.json(docker_auth),
        },
    )


# Debugging Asset
enable = False
if enable:

    @asset(
        ins={
            "group_out_base": AssetIn(
                AssetKey(["OpenStudioLandscapes_Base", "group_out_base"])
            ),
            "kitsu_group_in": AssetIn(
                AssetKey(["OpenStudioLandscapes_Kitsu", "group_in"])
            ),
            "kitsu_feature_out": AssetIn(
                AssetKey(["OpenStudioLandscapes_Kitsu", "feature_out"])
            ),
            # "watchtower_group_in": AssetIn(AssetKey(["OpenStudioLandscapes_Watchtower", "group_in"])),
            # "watchtower_feature_out": AssetIn(AssetKey(["OpenStudioLandscapes_Watchtower", "feature_out"])),
        },
    )
    def compare(
        context: AssetExecutionContext,
        **kwargs: dict,
    ):

        context.log.error(f"{kwargs = }")

        yield Output(kwargs)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                # "__".join(context.asset_key.path): MetadataValue.json(
                #     kwargs
                # ),
                "kwargs": MetadataValue.md(
                    f"```json\n{json.dumps(kwargs, indent=2, default=str)}\n```"
                ),
                "kwargs_keys": MetadataValue.md(
                    f"```json\n{json.dumps(list(kwargs.keys()), indent=2, default=str)}\n```"
                ),
                "group_out_base": MetadataValue.md(
                    f"```json\n{json.dumps(kwargs['group_out_base'], indent=2, default=str)}\n```"
                ),
                "group_out_base_keys": MetadataValue.md(
                    f"```json\n{json.dumps(list(kwargs['group_out_base'].keys()), indent=2, default=str)}\n```"
                ),
                "kitsu_feature_out": MetadataValue.md(
                    f"```json\n{json.dumps(kwargs['kitsu_feature_out'], indent=2, default=str)}\n```"
                ),
                "kitsu_feature_out_keys": MetadataValue.md(
                    f"```json\n{json.dumps(list(kwargs['kitsu_feature_out'].keys()), indent=2, default=str)}\n```"
                ),
                "watchtower_group_in": MetadataValue.md(
                    f"```json\n{json.dumps(kwargs['watchtower_group_in'], indent=2, default=str)}\n```"
                ),
                "watchtower_group_in_keys": MetadataValue.md(
                    f"```json\n{json.dumps(list(kwargs['watchtower_group_in'].keys()), indent=2, default=str)}\n```"
                ),
                "watchtower_feature_out": MetadataValue.md(
                    f"```json\n{json.dumps(kwargs['watchtower_feature_out'], indent=2, default=str)}\n```"
                ),
                "watchtower_feature_out_keys": MetadataValue.md(
                    f"```json\n{json.dumps(list(kwargs['watchtower_feature_out'].keys()), indent=2, default=str)}\n```"
                ),
            },
        )
