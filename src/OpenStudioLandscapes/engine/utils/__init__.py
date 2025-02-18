import pathlib
import shlex
import shutil

import git

from dagster import MetadataValue
from OpenStudioLandscapes.engine.constants import *

__all__ = [
    "compile_cmds",
    "cmd_list_to_str",
    "get_pip_install_str",
    "get_apt_install_str",
    "get_wget_str",
    "get_copy_str",
    "get_git_root",
]


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
            "RUN apt-get install -y --no-install-recommends '%s'\n" % apt_package
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
        wget_str += "RUN wget -O '%s' '%s'\n" % (wget_package, wget_url)
        if chmod_plus_x:
            wget_str += "RUN chmod a+x '%s'\n" % wget_package

    return wget_str


def get_git_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    print(git_root)
    return pathlib.Path(git_root)
