__all__ = [
    # "compile_cmds",
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
    "iterate_fds",
    "get_compose_scope",
    "get_feature_config",
    "expand_dict_vars",
]


import pathlib
import shlex
# import shutil
import select
from typing import MutableMapping, List, Any, Optional, IO

import git
from dagster import MetadataValue, AssetExecutionContext

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.exceptions import ComposeScopeException


# def compile_cmds(
#     docker_file,
#     tag,
#     volumes: [List, None] = None,
#     networks: [List, None] = None,
# ) -> MutableMapping[str, MetadataValue]:
#
#     if volumes is None:
#         volumes = []
#
#     if networks is None:
#         networks = []
#
#     _volumes = " ".join([f"--volume {i}" for i in volumes])
#     _networks = " ".join([f"--network {i}" for i in networks])
#
#     cmd_docker_run = [
#         shutil.which("docker"),
#         "run",
#         "--rm",
#         "--interactive",
#         "--tty",
#         "--entrypoint",
#         "bash",
#         tag,
#     ]
#
#     if bool(_volumes):
#         cmd_docker_run.insert(2, _volumes)
#
#     if bool(_networks):
#         cmd_docker_run.insert(2, _networks)
#
#     cmd_docker_build = [
#         shutil.which("docker"),
#         "build",
#         "--tag",
#         tag,
#         docker_file.parent.as_posix(),
#     ]
#
#     if not DOCKER_USE_CACHE:
#         cmd_docker_build.append("--no-cache")
#
#     metadata_values = {
#         "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
#         "cmd_docker_build": MetadataValue.path(cmd_list_to_str(cmd_docker_build)),
#     }
#
#     return metadata_values


def cmd_list_to_str(
    cmd_list: List[str],
) -> str:
    cmd_str = " ".join(shlex.quote(s) for s in cmd_list)
    return cmd_str


def get_pip_install_str(
    pip_install_packages: List[str],
) -> str:
    pip_install_str: str = str()
    for pip_package in pip_install_packages:
        pip_install_str += (
            "RUN python{PYTHON_MAJ}.{PYTHON_MIN} -m pip install --root-user-action=ignore '%s'\n"
            % pip_package
        )

    return pip_install_str


def get_apt_install_str(
    apt_install_packages: List[str],
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
    copy_packages: MutableMapping[str, str],
    mode: [int | None] = None,
) -> str:
    # Todo:
    #  - [ ] COPY vs. ADD?
    copy_str: str = str()
    # --chmod is a buildx feature. Trying to avoid that because
    # buildx is causing problems if the registry is only reachable
    # by inscure HTTP
    # _mode = "" if mode is None else f"--chmod={str(mode).zfill(4)}"
    _mode = "" if mode is None else str(mode).zfill(4)
    for copy_package in copy_packages.keys():
        copy_str += f"COPY ./{pathlib.Path(temp_dir).name}/{copy_package} .\n"
        if bool(_mode):
            copy_str += f"RUN chmod {str(mode).zfill(4)} {copy_package}\n"

    return copy_str


def get_wget_str(
    wget_packages: MutableMapping[str, str],
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
    # configs_root: pathlib.Path = pathlib.Path("{DOT_FEATURES}", "{FEATURE}", ".payload", "config")
    return configs_root


def get_data_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_root: pathlib.Path = get_git_root(path)
    data_root: pathlib.Path = git_root / ".payload" / "data"
    # data_root: pathlib.Path = pathlib.Path("{DOT_FEATURES}", "{FEATURE}", ".payload", "data")
    return data_root


def get_bin_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_root: pathlib.Path = get_git_root(path)
    bin_root: pathlib.Path = git_root / ".payload" / "bin"
    # bin_root: pathlib.Path = pathlib.Path("{DOT_FEATURES}", "{FEATURE}", ".payload", "bin")
    return bin_root


def get_image_name(
    context: AssetExecutionContext,
) -> str:
    return "_".join(context.asset_key.path).lower()


def parse_docker_image_path(
    *,
    docker_config: [DockerConfig, MutableMapping],
    prepend_registry: bool = True,
) -> str:

    image_path = []

    if isinstance(docker_config, DockerConfig):
        _docker_config: MutableMapping = docker_config.value
    elif isinstance(docker_config, MutableMapping):
        _docker_config: MutableMapping = docker_config
    else:
        raise TypeError

    _repository_name = _docker_config["docker_repository"]
    _docker_registry_url = _docker_config["docker_registry_url"]
    _repository_port = _docker_config["docker_registry_port"]

    if bool(prepend_registry):
        if bool(_docker_registry_url):
            image_path.append(_docker_registry_url)

            if bool(_repository_port):
                image_path.append(":")
                image_path.append(_repository_port)

            image_path.append("/")

    if bool(_repository_name):
        image_path.append(_repository_name)
        image_path.append("/")

    return str().join(image_path)


def iterate_fds(
        *,
        handles: tuple[
            Optional[IO[bytes]],
            Optional[IO[bytes]],
        ],
        labels: tuple[str, str],
        functions: tuple[
            callable, callable,
        ],
        live_print=False,
) -> MutableMapping[str, bytes]:
    """
    Can be used to live-feed stdout and stderr of a
    subprocess.Popen.stdout/stderr stream to an
    appropriate logging stream like info and warning.
    stdout -> logging.info
    stderr -> logging.warning

    Usage:

    ```
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stream_logs = True

    handles = (proc.stdout, proc.stderr)
    labels = ("stdout", "stderr")
    functions = (context.log.info, context.log.warning)
    logs = helpers.iterate_fds(
        handles=handles,
        labels=labels,
        functions=functions,
        live_print=stream_logs
    )

    if stream_logs:
        for _label, _function in zip(labels, functions):
            if bool(logs[_label]):
                _function(logs[_label].decode("utf-8"))
    ```

    Reference:

    https://alexandre.deverteuil.net/post/monitor-python-subprocess-output-streams-real-time/

    Args:
        handles (tuple[
                typing.Optional[typing.IO[bytes]],
                typing.Optional[typing.IO[bytes]],
            ]): io.BufferedReader
        labels (tuple[str, str]):
        functions (tuple[
                callable, callable,
            ]): bound method (Logger.info, Logger.warning)
        live_print (bool): Do you want to live_print? (False is equivalent to "summarize")

    Returns: dict[callable, bytes]

    """

    ret = {}

    for label in labels:
        ret[label] = bytes()

    methods = dict(zip(handles, zip(labels, functions)))

    while methods:
        for handle in select.select(methods.keys(), tuple(), tuple())[0]:

            label = methods[handle][0]
            function = methods[handle][1]
            line = handle.readline()

            if line:
                if live_print:
                    function(line.decode("utf-8"))
                ret[label] += line

                # This is from the reference, but can't
                # tell the difference so far other than
                # not cutting off the last character in
                # a line without \n
                # methods[handle](line[:-1].decode("utf-8"))
            else:
                methods.pop(handle)

    return ret


def get_compose_scope(
        context: AssetExecutionContext,
        features: MutableMapping,
        name: str,
) -> ComposeScope:

    feature_keys = features.keys()

    _module = name
    _parent = ".".join(_module.split(".")[:-1])
    _definitions = ".".join([_parent, "definitions"])

    COMPOSE_SCOPE = None
    for key in feature_keys:
        if features[key]["module"] == _definitions:
            COMPOSE_SCOPE: ComposeScope = features[key]["compose_scope"]
            break

    if COMPOSE_SCOPE is None:
        raise ComposeScopeException(
            "No compose_scope found for module '%s'. Is the module enabled "
            "in `OpenStudioLandscapes.engine.constants.FEATURES` and/or did "
            "you re-execute the Dagster tree?" % _module
        )
    return COMPOSE_SCOPE


def get_feature_config(
        context: AssetExecutionContext,
        features: MutableMapping,
        name: str,
) -> Any | None:

    feature_keys = features.keys()

    _module = name
    _parent = ".".join(_module.split(".")[:-1])
    _definitions = ".".join([_parent, "definitions"])

    FEATURE_CONFIG = None
    for key in feature_keys:
        if features[key]["module"] == _definitions:
            FEATURE_CONFIG = features[key].get(
                "feature_config", OpenStudioLandscapesConfig.DEFAULT
            )
            context.log.info(
                "feature_config for Feature %s is set to: \n%s."
                % (features[key]["module"], FEATURE_CONFIG)
            )
            break
    return FEATURE_CONFIG


def expand_dict_vars(
        dict_to_expand: MutableMapping,
        kv: MutableMapping,
) -> MutableMapping:
    """
    This helper expands key-value pairs into the
    string.format()-formatted value of a dictionary.

    i.e. a string like:
    `{DOT_LANDSCAPES}/{LANDSCAPE}/Kitsu__Kitsu/data/kitsu`

    will be expanded as follows:
    `/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-16-14-14-36-903f4b8a760547a2b1e6cafed4551f6e/Kitsu__Kitsu/data/kitsu`

    using the key-value pairs
    ```
    {
        "DOT_LANDSCAPES": "/home/michael/git/repos/OpenStudioLandscapes/.landscapes",
        "LANDSCAPE": "2025-04-16-14-14-36-903f4b8a760547a2b1e6cafed4551f6e",
    }
    ```
    """

    for k, v in dict_to_expand.items():
        if isinstance(v, str):
            dict_to_expand[k] = v.format(**kv)

    return dict_to_expand
