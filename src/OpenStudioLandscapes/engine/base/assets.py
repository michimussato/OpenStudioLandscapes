import base64
import json
import pathlib
import shutil
import textwrap
from pathlib import Path

import time
import urllib.parse
from typing import Generator, MutableMapping, List, Any

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import DockerConfig, DockerRepositoryType
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.docker import *


@asset(
    **ASSET_HEADER_BASE,
)
def pip_packages(
    context: AssetExecutionContext,
) -> Generator[Output[List] | AssetMaterialization, None, None]:
    """ """

    _pip_packages: list = [
        # Content moved to OpenStudioLandscapes.Dagster.assets.pip_packages
        # Todo:
        #  - [ ] enable OpenStudioLandscapes after making it public
        #  - [x] maybe move dagster stuff to dagster image?
    ]

    yield Output(_pip_packages)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_pip_packages),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
)
def apt_packages(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _apt_packages = {}

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
        "iproute2",
        "liblzma-dev",
    ]

    yield Output(_apt_packages)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_apt_packages),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "docker_config": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "DOCKER_CONFIG"])),
        "docker_config_json": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "docker_config_json"])),
        "write_dockerfile": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "write_dockerfile"])),
    },
)
def build_docker_image(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
    write_dockerfile: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | list[str]]] | AssetMaterialization, None, None]:
    """ """

    docker_file = write_dockerfile

    # shutil.rmtree(docker_file.parent, ignore_errors=True)
    #
    # docker_file.parent.mkdir(parents=True, exist_ok=True)

    image_name = get_image_name(context=context)
    image_prefix_local = parse_docker_image_path(
        docker_config=docker_config,
        prepend_registry=False,
    )
    image_prefix_full = parse_docker_image_path(
        docker_config=docker_config,
        prepend_registry=True,
    )

    tags = [
        env.get('LANDSCAPE', str(time.time())),
    ]

    image_data = {
        "image_name": image_name,
        "image_prefix_local": image_prefix_local,
        "image_prefix_full": image_prefix_full,
        "image_tags": tags,
        "image_parent": {},
    }

    context.log.info(f"{image_data = }")

    # Full command as per python-on-whales
    # Build command (public) (OK: [x]):  /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json build --quiet --pull --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles/Dockerfile --no-cache --tag openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9 --tag harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9 /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles
    # Push command (public):             /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json image push harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-04-29-00-43-06-aa6a607169ea49138c242967c00bb7e9
    # Build command (private) (OK: [x]): /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json build --quiet --pull --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles/Dockerfile --no-cache --tag openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666 --tag harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666 /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__build_docker_image/Dockerfiles
    # Push command (private):            /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json image push harbor.farm.evil:80/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-05-02-10-53-11-b9aaea217caf4017a403fc001a5cd666

    cmds = []

    tags_local = [f"{image_prefix_local}{image_name}:{tag}" for tag in tags]
    tags_full = [f"{image_prefix_full}{image_name}:{tag}" for tag in tags]

    cmd_build = docker_build_cmd(
        context=context,
        docker_config_json=docker_config_json,
        docker_file=docker_file,
        tags_local=tags_local,
        tags_full=tags_full,
    )

    cmds.append(cmd_build)

    cmds_push = docker_push_cmd(
        context=context,
        docker_config_json=docker_config_json,
        tags_full=tags_full,
    )

    cmds.extend(cmds_push)

    context.log.info(f"{cmds = }")

    logs = []

    for logs_ in docker_process_cmds(
        context=context,
        cmds=cmds,
    ):
        logs.append(logs_)

    yield Output(image_data)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(image_data),
            "env": MetadataValue.json(env),
            "logs": MetadataValue.json(logs),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "apt_packages": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "apt_packages"])),
        "pip_packages": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "pip_packages"])),
    },
)
def write_dockerfile(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    apt_packages: dict[str, list[str]],  # pylint: disable=redefined-outer-name
    pip_packages: list,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path] | AssetMaterialization | Any, Any, None]:
    """ """

    docker_file = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{ASSET_HEADER_BASE['group_name']}__{'__'.join(ASSET_HEADER_BASE['key_prefix'])}",
        "__".join(context.asset_key.path),
        "Dockerfiles",
        "Dockerfile",
    )

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    image_name = get_image_name(context=context)

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

        RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --upgrade pip setuptools setuptools_scm wheel

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
            "__".join(context.asset_key.path): MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    tags={
        "group_out": "base",
    },
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "constants_base": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "constants_base"])),
        "docker_config": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "DOCKER_CONFIG"])),
        "docker_config_json": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "docker_config_json"])),
        "features": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "features"])),
        "build_docker_image": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "build_docker_image"]),
        ),
    },
)
def group_out_base(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    constants_base: dict,  # pylint: disable=redefined-outer-name
    # Todo:
    #  - [ ] Probably not needed with the docker config.json specified
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
    features: dict,  # pylint: disable=redefined-outer-name
    build_docker_image: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | dict]] | AssetMaterialization, None, None]:

    out_dict: dict = {}

    out_dict["env"] = env
    out_dict["env_base"] = env
    out_dict["constants_base"] = constants_base
    out_dict["docker_config"] = docker_config
    out_dict["docker_config_json"] = docker_config_json
    out_dict["features"] = features
    out_dict["docker_image"] = build_docker_image

    yield Output(out_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "env": MetadataValue.json(env),
            "env_base": MetadataValue.json(env),
            "constants_base": MetadataValue.json(constants_base),
            "docker_config": MetadataValue.json(docker_config.value),
            "docker_config_json": MetadataValue.path(docker_config_json),
            "features": MetadataValue.json(features),
            "docker_image": MetadataValue.json(build_docker_image),
        },
    )



@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "docker_config": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "DOCKER_CONFIG"])),
        # "constants_base": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "constants_base"])),
        # "docker_config": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "DOCKER_CONFIG"])),
        # "features": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "features"])),
        # "build_docker_image": AssetIn(
        #     AssetKey([*ASSET_HEADER_BASE["key_prefix"], "build_docker_image"]),
        # ),
    },
)
def docker_config_json(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    context.log.info(f"{dir(docker_config.value) = }")

    login_required: bool = docker_config.value["docker_repository_type"] == DockerRepositoryType.PRIVATE
    context.log.debug(f"{login_required = }")

    dockercfg_path = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{ASSET_HEADER_BASE['group_name']}__{'__'.join(ASSET_HEADER_BASE['key_prefix'])}",
        "__".join(context.asset_key.path),
        "config.json",
    )

    dockercfg_path.parent.mkdir(parents=True, exist_ok=True)

    docker_auth = {}
    docker_auth["auths"] = auths = {}

    # process from docker/api/config.py:create_config
    # (https://docker-py.readthedocs.io/en/stable/api.html#docker.api.config.ConfigApiMixin.create_config)
    username: str = docker_config.value["docker_registry_username"]
    password: str = docker_config.value["docker_registry_password"]
    url_: str = docker_config.value["docker_registry_url"]
    port_: str = docker_config.value["docker_registry_port"]
    # url: str = f"http://{url_}:{port_}"

    credentials_str = f"{username}:{password}"
    credentials_bytes = credentials_str.encode("utf-8")
    credentials_encoded = base64.b64encode(credentials_bytes).decode("ascii")

    auths[f"{url_}:{port_}"] = {
        "auth": credentials_encoded
    }

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
            "__".join(context.asset_key.path): MetadataValue.path(dockercfg_path.parent),
            "config_json": MetadataValue.path(dockercfg_path),
            "docker_auth": MetadataValue.json(docker_auth),
        },
    )
