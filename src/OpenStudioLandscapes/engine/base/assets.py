import pathlib
import shutil
import textwrap
import time
import urllib.parse
from typing import Generator

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import DockerConfig
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.docker.whales import *


@asset(
    **ASSET_HEADER_BASE,
)
def pip_packages(
    context: AssetExecutionContext,
) -> Generator[Output[list] | AssetMaterialization, None, None]:
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
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
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
        "env": AssetIn(AssetKey([*KEY_BASE_ENV, "env"])),
        "docker_config": AssetIn(AssetKey([*KEY_BASE_ENV, "DOCKER_CONFIG"])),
        "apt_packages": AssetIn(AssetKey([*KEY_BASE, "apt_packages"])),
        "pip_packages": AssetIn(AssetKey([*KEY_BASE, "pip_packages"])),
    },
)
def build_docker_image(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
    apt_packages: dict[str, list[str]],  # pylint: disable=redefined-outer-name
    pip_packages: list,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | list[str]]] | AssetMaterialization, None, None]:
    """ """

    docker_file = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{GROUP_BASE}__{'__'.join(KEY_BASE)}",
        "__".join(context.asset_key.path),
        "Dockerfiles",
        "Dockerfile",
    )

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

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
        image_name=image_name,
        **env,
    )
    # @formatter:on

    with open(docker_file, mode="w", encoding="utf-8") as fw:
        fw.write(docker_file_str)

    with open(docker_file, mode="r") as fr:
        docker_file_content = fr.read()

    image_data = {
        "image_name": image_name,
        "image_prefix_local": image_prefix_local,
        "image_prefix_full": image_prefix_full,
        "image_tags": tags,
        "image_parent": {},
    }

    context.log.info(image_data)

    tags_list: list = docker_build(
        context=context,
        docker_config=docker_config,
        docker_file=docker_file,
        context_path=docker_file.parent,
        docker_use_cache=DOCKER_USE_CACHE_BASE,
        image_data=image_data,
    )

    yield Output(image_data)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(image_data),
            "tags_list": MetadataValue.json(tags_list),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    tags={
        "group_out": "base",
    },
    ins={
        "env": AssetIn(AssetKey([*KEY_BASE_ENV, "env"])),
        "constants_base": AssetIn(AssetKey([*KEY_BASE_ENV, "constants_base"])),
        "docker_config": AssetIn(AssetKey([*KEY_BASE_ENV, "DOCKER_CONFIG"])),
        "features": AssetIn(AssetKey([*KEY_BASE_ENV, "features"])),
        "build_docker_image": AssetIn(
            AssetKey([*KEY_BASE, "build_docker_image"]),
        ),
    },
)
def group_out(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    constants_base: dict,  # pylint: disable=redefined-outer-name
    docker_config: DockerConfig,  # pylint: disable=redefined-outer-name
    features: dict,  # pylint: disable=redefined-outer-name
    build_docker_image: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | dict]] | AssetMaterialization, None, None]:

    out_dict: dict = {}

    out_dict["env"] = env
    out_dict["env_base"] = env
    out_dict["constants_base"] = constants_base
    out_dict["docker_config"] = docker_config
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
            "features": MetadataValue.json(features),
            "docker_image": MetadataValue.json(build_docker_image),
        },
    )
