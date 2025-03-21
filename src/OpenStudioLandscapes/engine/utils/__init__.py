__all__ = [
    "compile_cmds",
    "cmd_list_to_str",
    "get_pip_install_str",
    "get_apt_install_str",
    "get_wget_str",
    "get_copy_str",
    "get_git_root",
    "get_configs_root",
    "get_data_root",
    "get_bin_root",
    "get_image_name",
    "parse_docker_image_path",
]


import pathlib
import shlex
import shutil

import git
from dagster import MetadataValue, AssetExecutionContext

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *


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

    _volumes = " ".join([f"--volume {i}" for i in volumes])
    _networks = " ".join([f"--network {i}" for i in networks])

    cmd_docker_run = [
        shutil.which("docker"),
        "run",
        "--rm",
        "--interactive",
        "--tty",
        "--entrypoint",
        "bash",
        tag,
    ]

    if bool(_volumes):
        cmd_docker_run.insert(2, _volumes)

    if bool(_networks):
        cmd_docker_run.insert(2, _networks)

    cmd_docker_build = [
        shutil.which("docker"),
        "build",
        "--tag",
        tag,
        docker_file.parent.as_posix(),
    ]

    if not DOCKER_USE_CACHE:
        cmd_docker_build.append("--no-cache")

    metadata_values = {
        "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        "cmd_docker_build": MetadataValue.path(cmd_list_to_str(cmd_docker_build)),
    }

    return metadata_values


def cmd_list_to_str(
    cmd_list: list[str],
) -> str:
    cmd_str = " ".join(shlex.quote(s) for s in cmd_list)
    return cmd_str


def get_pip_install_str(
    pip_install_packages: list[str],
) -> str:
    pip_install_str: str = str()
    for pip_package in pip_install_packages:
        pip_install_str += (
            "RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore '%s'\n"
            % pip_package
        )

    return pip_install_str


def get_apt_install_str(
    apt_install_packages: list[str],
) -> str:
    apt_install_str: str = str()
    for apt_package in apt_install_packages:
        apt_install_str += (
            # "RUN apt-get install -y --no-install-recommends '%s'\n" % apt_package
            f"RUN apt-get install -y --no-install-recommends '{apt_package}'\n"
        )

    return apt_install_str


def get_copy_str(
    temp_dir: str,
    copy_packages: dict[str, str],
    mode: [int | None] = None,
) -> str:
    # Todo:
    #  - [ ] COPY vs. ADD?
    copy_str: str = str()
    _mode = "" if mode is None else f"--chmod={str(mode).zfill(4)}"
    for copy_package in copy_packages.keys():
        copy_str += f"COPY {_mode} ./{pathlib.Path(temp_dir).name}/{copy_package} .\n"

    return copy_str


def get_wget_str(
    wget_packages: dict[str, str],
    chmod_plus_x: bool = True,
) -> str:
    wget_str: str = str()
    for wget_package, wget_url in wget_packages.items():
        # wget_str += "RUN wget -O '%s' '%s'\n" % (wget_package, wget_url)
        wget_str += f"RUN wget -O '{wget_package}' '{wget_url}'\n"
        if chmod_plus_x:
            # wget_str += "RUN chmod a+x '%s'\n" % wget_package
            wget_str += f"RUN chmod a+x '{wget_package}'\n"

    return wget_str


def get_git_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    """Get the Git base path of a file which is lives inside a repository."""
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return pathlib.Path(git_root)


def get_configs_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_root: pathlib.Path = get_git_root(path)
    configs_root: pathlib.Path = git_root / ".payload" / "config"
    return configs_root


def get_data_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_root: pathlib.Path = get_git_root(path)
    data_root: pathlib.Path = git_root / ".payload" / "data"
    return data_root


def get_bin_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_root: pathlib.Path = get_git_root(path)
    bin_root: pathlib.Path = git_root / ".payload" / "bin"
    return bin_root


def get_image_name(
    context: AssetExecutionContext,
) -> str:
    return "_".join(context.asset_key.path).lower()


# def get_compose_network(
#     network_dict: dict,
#     network_mode: ComposeNetworkMode = ComposeNetworkMode.DEFAULT,
# ) -> NotImplementedError:
#     raise NotImplementedError


def parse_docker_image_path(
    image_name: str,
    docker_config: [DockerConfig, dict],
    tag: str = None,
) -> str:

    if tag is not None:
        image_name = f"{image_name}:{tag}"

    if isinstance(docker_config, DockerConfig):
        _docker_config: dict = docker_config.value
    elif isinstance(docker_config, dict):
        _docker_config: dict = docker_config
    else:
        raise TypeError

    _repository_name = _docker_config.get("docker_repository", None)
    if bool(_repository_name):
        repository_name = f"{_repository_name}/"
    else:
        repository_name = ""

    if _docker_config["docker_use_local"]:
        return f"{repository_name}{image_name}"

    else:
        # docker.io is the docker default in none is explicitly specified
        _docker_registry_url = _docker_config.get("docker_registry_url", "docker.io")
        _docker_registry_port = _docker_config.get("docker_registry_port", None)
        if bool(_docker_registry_port):
            docker_registry = f"{_docker_registry_url}:{_docker_registry_port}/"
        else:
            docker_registry = f"{_docker_registry_url}/"

        return f"{docker_registry}{repository_name}{image_name}"
