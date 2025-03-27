import getpass
import pathlib
import shutil
import socket
import textwrap
import time
import urllib.parse
import uuid
from datetime import datetime
from typing import Generator

from python_on_whales import Builder

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.constants import *
# from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.docker.whales import *


@asset(
    **ASSET_HEADER_BASE,
)
def git_root(
    context: AssetExecutionContext,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    _git_root = get_git_root()

    yield Output(_git_root)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_git_root),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
)
def landscape_id(
    context: AssetExecutionContext,
) -> Generator[Output[dict[str, str]] | AssetMaterialization, None, None]:

    now = datetime.now()

    landscape_stamp = {
        "LANDSCAPE": f"{datetime.strftime(now, '%Y-%m-%d_%H-%M-%S')}__{uuid.uuid4().hex}".replace("__", "_").replace("_", "-"),
    }

    yield Output(landscape_stamp)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(landscape_stamp),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
)
def secrets(
    context: AssetExecutionContext,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
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
    **ASSET_HEADER_BASE,
    ins={
        "git_root": AssetIn(
            AssetKey([*KEY_BASE, "git_root"]),
        ),
    },
)
def dot_landscapes(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    _dot_landscapes = git_root / ".landscapes"
    _dot_landscapes.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield Output(_dot_landscapes)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_dot_landscapes),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    ins={
        "git_root": AssetIn(AssetKey([*KEY_BASE, "git_root"])),
        "secrets": AssetIn(AssetKey([*KEY_BASE, "secrets"])),
        "landscape_id": AssetIn(AssetKey([*KEY_BASE, "landscape_id"])),
        "dot_landscapes": AssetIn(AssetKey([*KEY_BASE, "dot_landscapes"])),
        "nfs": AssetIn(AssetKey([*KEY_BASE, "nfs"])),
    },
    deps=[
        AssetKey(
            [
                *ASSET_HEADER_BASE["key_prefix"],
                f"constants_{ASSET_HEADER_BASE['group_name']}",
            ]
        )
    ],
)
def env(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
    secrets: dict,  # pylint: disable=redefined-outer-name
    landscape_id: dict,  # pylint: disable=redefined-outer-name
    dot_landscapes: pathlib.Path,  # pylint: disable=redefined-outer-name
    nfs: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    # @formatter:off
    # Todo
    #  - [ ] Move to constants.py
    ENVIRONMENT_BASE: dict = {
        "GIT_ROOT": git_root.as_posix(),
        # Todo
        #  - [ ] Move CONFIGS_ROOT to individual modules
        "CONFIGS_ROOT": pathlib.Path(
            git_root,
            "configs",
        ).as_posix(),
        "DOT_LANDSCAPES": dot_landscapes.as_posix(),
        "AUTHOR": "michimussato@gmail.com",
        "CREATED_BY": str(getpass.getuser()),
        "CREATED_ON": str(socket.gethostname()),
        "CREATED_AT": str(datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")),
        "TIMEZONE": "Europe/Zurich",
        # "IMAGE_PREFIX": "michimussato",
        "DEFAULT_CONFIG_DBPATH": "/data/configdb",
        "ROOT_DOMAIN": "farm.evil",
        # https://vfxplatform.com/
        "PYTHON_MAJ": "3",
        "PYTHON_MIN": "11",
        "PYTHON_PAT": "11",
    }

    ENVIRONMENT_BASE.update(secrets)
    ENVIRONMENT_BASE.update(landscape_id)
    ENVIRONMENT_BASE.update(nfs)
    # @formatter:on

    yield Output(ENVIRONMENT_BASE)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ENVIRONMENT_BASE),
            # "ENVIRONMENT_BASE": MetadataValue.json(ENVIRONMENT_BASE),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
)
def pip_packages(
    context: AssetExecutionContext,
) -> Generator[Output[list] | AssetMaterialization, None, None]:
    """ """

    _pip_packages: list = [
        # Todo:
        #  - [ ] enable OpenStudioLandscapes after making it public
        #  - [ ] maybe move dagster stuff to dagster image?
        # "OpenStudioLandscapes[dev] @ git+https://github.com/michimussato/OpenStudioLandscapes.git@main",
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


deps_ = []
if DOCKER_CONFIG.value["docker_use_local"]:
    deps_.append(
        AssetKey([*KEY_BASE, "write_registry_env"])
    )
@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*KEY_BASE, "env"])),
        "apt_packages": AssetIn(AssetKey([*KEY_BASE, "apt_packages"])),
        "pip_packages": AssetIn(AssetKey([*KEY_BASE, "pip_packages"])),
        "run_builder": AssetIn(AssetKey([*KEY_BASE, "run_builder"])),
    },
    deps=deps_,
)
def build_docker_image(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    apt_packages: dict[str, list[str]],  # pylint: disable=redefined-outer-name
    pip_packages: list,  # pylint: disable=redefined-outer-name
    run_builder: Builder,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | list[str]]] | AssetMaterialization, None, None]:
    """ """

    docker_config = DOCKER_CONFIG

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
        docker_use_cache=DOCKER_USE_CACHE,
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
)
def nfs(
    context: AssetExecutionContext,
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
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
    **ASSET_HEADER_BASE,
    tags={
        "group_out": "base",
    },
    ins={
        "env": AssetIn(AssetKey([*KEY_BASE, "env"])),
        "run_builder": AssetIn(AssetKey([*KEY_BASE, "run_builder"])),
        "build_docker_image": AssetIn(
            AssetKey([*KEY_BASE, "build_docker_image"]),
        ),
    },
)
def group_out(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    run_builder: Builder,  # pylint: disable=redefined-outer-name
    build_docker_image: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | dict]] | AssetMaterialization, None, None]:

    out_dict: dict = {}

    out_dict["env"] = env
    out_dict["docker_config"] = DOCKER_CONFIG
    out_dict["docker_builder"] = run_builder
    out_dict["docker_image"] = build_docker_image

    yield Output(out_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "env": MetadataValue.json(env),
            "run_builder": MetadataValue.path(run_builder.name),
            "docker_image": MetadataValue.json(build_docker_image),
        },
    )
