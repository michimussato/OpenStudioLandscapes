import base64
import json
import pathlib
import shutil
import textwrap
import time
import urllib.parse
from typing import Generator, List, MutableMapping

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.config.models import DockerConfigModel, ConfigEngine
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.policies.retry import build_docker_image_retry_policy
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.docker import *
from OpenStudioLandscapes.engine.config import dist


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
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])
        ),
        "docker_config_json": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "docker_config_json"])
        ),
        "apt_packages": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "apt_packages"])
        ),
        "pip_packages": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "pip_packages"])
        ),
    },
    retry_policy=build_docker_image_retry_policy,
)
def build_docker_image(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    CONFIG: ConfigEngine,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
    apt_packages: dict[str, list[str]],  # pylint: disable=redefined-outer-name
    pip_packages: list,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | list[str]]] | AssetMaterialization, None, None]:
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
        apt_install_packages=apt_packages["base"],
    )

    apt_install_str_build_python311: str = get_apt_install_str(
        apt_install_packages=apt_packages["build_python311"],
    )

    pip_install_str: str = get_pip_install_str(pip_install_packages=pip_packages)

    # @formatter:off
    docker_file_str = textwrap.dedent(
        """\
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

    image_data = {
        "image_name": image_name,
        "image_prefixes": image_prefixes,
        "image_tags": tags,
        "image_parent": {},
    }

    # just highlight the message
    context.log.warning(f"{image_data = }")

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
        docker_file=docker_file,
        tags=tags_full_str,
        pull=docker_config.use_registry and docker_config.docker_registry_config.docker_pull,
        no_cache=docker_config.no_cache,
    )

    cmds.append(cmd_build)

    if docker_config.use_registry \
            and docker_config.docker_registry_config.docker_push :  # or not_push
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
            docker_file.name: MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            "env": MetadataValue.json(env),
            "logs": MetadataValue.json(logs),
        },
    )


@asset(
    **ASSET_HEADER_BASE,
    # Todo:
    #  - [ ] still necessary?
    tags={
        "group_out": "base",
    },
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])
        ),
        "docker_config_json": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "docker_config_json"])
        ),
        "build_docker_image": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], "build_docker_image"]),
        ),
    },
    description=textwrap.dedent(
        """
        This is the foundation. This assets provides all relevant environment information
        for subsequent assets and asset groups. All downstream assets consume this data and
        build their environment on top of this.
        """
    ),
)
def group_out_base(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    CONFIG: ConfigEngine,  # pylint: disable=redefined-outer-name
    docker_config_json: pathlib.Path,  # pylint: disable=redefined-outer-name
    build_docker_image: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str | dict]] | AssetMaterialization, None, None]:

    out_dict: dict = {}

    docker_config: DockerConfigModel = CONFIG.openstudiolandscapes__docker_config

    out_dict["env"] = env
    out_dict["env_base"] = env
    out_dict["config_engine"]: ConfigEngine = CONFIG
    out_dict["docker_config"] = docker_config.docker_registry_config.model_dump()
    out_dict["docker_config"]["docker_repository"] = docker_config.docker_registry_config.docker_repository_name
    out_dict["docker_config"]["docker_repository_type"] = docker_config.docker_registry_config.docker_registry_access
    out_dict["docker_config"]["docker_registry_url"] = docker_config.docker_registry_config.docker_registry_fqdn
    out_dict["docker_config"]["docker_use_local"] = not docker_config.docker_registry_config.docker_push
    out_dict["docker_config_json"] = docker_config_json
    out_dict["docker_image"] = build_docker_image

    yield Output(out_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata=metadatavalues_from_dict(
            context=context,
            d_serialized=out_dict,
        )
    )


@asset(
    **ASSET_HEADER_BASE,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "CONFIG": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])
        ),
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
