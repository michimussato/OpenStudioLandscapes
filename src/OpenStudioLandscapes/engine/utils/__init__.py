__all__ = [
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
    "serialize_dict",
    "metadatavalues_from_dict",
    "get_relative_path_via_common_root",
    "get_bool_env",
    "get_str_env",
]

import os
import pathlib
import shlex
import select
from typing import MutableMapping, List, Any, Optional, IO, Union

import git
from dagster import AssetExecutionContext, MetadataValue, OpExecutionContext

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.exceptions import ComposeScopeException


def cmd_list_to_str(
    cmd_list: List[str],
) -> str:
    cmd_str = " ".join(shlex.quote(s) for s in cmd_list)
    return cmd_str


def get_pip_install_str(
    pip_install_packages: List[str],
    python_str: str = "python{PYTHON_MAJ}.{PYTHON_MIN}",
    single_layered: bool = True,
) -> str:
    pip_install_str: str = str()

    if single_layered:
        if bool(pip_install_packages):
            pip_install_str += "RUN %s -m pip install --root-user-action=ignore " % python_str
            for pip_package in pip_install_packages:
                pip_install_str += "'%s' " % pip_package
            pip_install_str += "\n"
    else:
        for pip_package in pip_install_packages:
            pip_install_str += (
                "RUN %s -m pip install --root-user-action=ignore '%s'\n"
                % (python_str, pip_package)
            )

    return pip_install_str


def get_apt_install_str(
    apt_install_packages: List[str],
    single_layered: bool = True,
) -> str:
    apt_install_str: str = str()

    if single_layered:
        if bool(apt_install_packages):
            apt_install_str += "RUN apt-get install -y --no-install-recommends "
            for apt_package in apt_install_packages:
                apt_install_str += f"'{apt_package}' "
            apt_install_str += "\n"
    else:
        for apt_package in apt_install_packages:
            apt_install_str += (
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


# Todo:
#  - [ ] deprecate?
def get_git_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    """Get the Git base path of a file which is lives inside a repository."""
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")
    return pathlib.Path(git_root)


# Todo:
#  - [ ] deprecate
def get_configs_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_root: pathlib.Path = get_git_root(path)
    configs_root: pathlib.Path = git_root / ".payload" / "config"
    # configs_root: pathlib.Path = pathlib.Path("{DOT_FEATURES}", "{FEATURE}", ".payload", "config")
    return configs_root


# Todo:
#  - [ ] deprecate
def get_data_root(
    path: pathlib.Path = pathlib.Path(__file__),
) -> pathlib.Path:
    git_root: pathlib.Path = get_git_root(path)
    data_root: pathlib.Path = git_root / ".payload" / "data"
    # data_root: pathlib.Path = pathlib.Path("{DOT_FEATURES}", "{FEATURE}", ".payload", "data")
    return data_root


# Todo:
#  - [ ] deprecate
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
) -> MutableMapping[str, list[str]]:
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

    for _label, _function in zip(labels, functions):
        if bool(logs[_label]):
            _function(logs[_label])
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

    Returns: MutableMapping[str, list[str]]

    """

    ret = {}

    for label in labels:
        ret[label] = []

    methods = dict(zip(handles, zip(labels, functions)))

    while methods:
        for handle in select.select(methods.keys(), tuple(), tuple())[0]:

            label = methods[handle][0]
            function = methods[handle][1]
            line = handle.readline()

            if line:
                line_ = line.decode("utf-8").rstrip()
                if live_print:
                    function(line_)
                ret[label].append(line_)

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


# JSON cannot serialize certain types
# out of the box. This makes sure that
# MetadataValue.json receives only
# serializable input.
# Serializes in place.
def serialize_dict(
        context: Union[AssetExecutionContext, OpExecutionContext],
        d: MutableMapping,
) -> None:

    for k_, v_ in d.items():
        if isinstance(v_, MutableMapping):
            serialize_dict(
                context=context,
                d=v_,
            )
        elif isinstance(v_, pathlib.PosixPath):
            d[k_] = v_.as_posix()
        # Todo:
        # elif isinstance(v_, enum.Enum):
        #     # RuntimeError: dictionary changed size during iteration
        #     d[v_.name] = v_.value
        # Todo:
        # elif isinstance(v_, List):
        #     pass
        else:
            d[k_] = str(v_)

    return None


# Just an idea, but was not successful so far:
# def serialize_dict(
#         context: AssetExecutionContext,
#         unserializable_dict: MutableMapping = None,
#         _serialized_dict: MutableMapping = None,
#         # _use_dict = None,
# ) -> MutableMapping:
#
#     # d_ = copy.deepcopy(d)
#     if _serialized_dict is None:
#         _serialized_dict = {}
#         dict_to_serialize = copy.deepcopy(unserializable_dict)
#     else:
#         dict_to_serialize = _serialized_dict
#     # else:
#     #     d_ = _use_dict
#
#     for k_, v_ in dict_to_serialize.items():
#         if isinstance(v_, MutableMapping):
#             serialize_dict(
#                 context=context,
#                 unserializable_dict=None,
#                 _serialized_dict=_serialized_dict,
#             )
#         elif isinstance(v_, pathlib.PosixPath):
#             _serialized_dict[k_] = v_.as_posix()
#         # Todo:
#         elif isinstance(v_, enum.Enum):
#             _serialized_dict[v_.name] = v_.value
#         # Todo:
#         # elif isinstance(v_, List):
#         #     pass
#         else:
#             _serialized_dict[k_] = v_
#
#     return _serialized_dict


def metadatavalues_from_dict(
        context: Union[AssetExecutionContext, OpExecutionContext],
        d_serialized: MutableMapping,
) -> MutableMapping[str, MetadataValue]:

    metadata = {}

    for k, v in d_serialized.items():
        metadata[k] = MetadataValue.json(v)

    context.log.debug(f"{metadata = }")

    return metadata


def get_relative_path_via_common_root(
        context: Union[AssetExecutionContext, OpExecutionContext],
        path_src: pathlib.Path,
        path_dst: pathlib.Path,
        path_common_root: pathlib.Path,
) -> pathlib.Path:
    """
    Returns a relative path from `path_src` to `path_dst` where `path_common_root`
    will be the common root.

    Args:
        context: Union[AssetExecutionContext, OpExecutionContext]
        path_src: pathlib.Path The starting point
        path_dst: pathlib.Path
        path_common_root: pathlib.Path

    Returns:
        pathlib.Path

    """
    # SRC:
    # path_src = pathlib.Path("/opt/openstudiolandscapes/.landscapes/2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929/ComposeScope_default__ComposeScope_default/ComposeScope_default__DOCKER_COMPOSE/docker_compose/docker-compose.yml")
    #
    # DST:
    # path_dst = pathlib.Path("/opt/openstudiolandscapes/.landscapes/2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929/Dagster__Dagster/Dagster__DOCKER_COMPOSE/docker_compose/docker-compose.yml")
    #
    # ROOT:
    # path_common_root = pathlib.Path("/opt/openstudiolandscapes/.landscapes/")

    context.log.debug(f"{path_src = }")
    context.log.debug(f"{path_dst = }")

    if not path_common_root.is_absolute():
        raise Exception(f"{path_common_root = } must be absolute.")

    common_root_name = path_common_root.name  # .landscapes
    common_root_parts = path_common_root.parts  # ('/', 'opt', 'openstudiolandscapes', '.landscapes')

    # Todo
    #  - [ ] What if common_root_name occurs multiple times?
    if not common_root_parts.count(common_root_name) == 1:
        raise Exception(f"{common_root_name = } occurs multiple times.")
    index_common_root_name = common_root_parts.index(common_root_name)  # 3
    # We don't want .landscapes to be part of the path: increment index by 1
    index_common_root_name += 1  # 4
    context.log.debug(f"{index_common_root_name = }")

    rel_path_src_from_common_root = path_src.parent.parts[index_common_root_name:]  # ('2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929', 'ComposeScope_default__ComposeScope_default', 'ComposeScope_default__DOCKER_COMPOSE', 'docker_compose')
    context.log.debug(f"{rel_path_src_from_common_root = }")
    rel_path_dst_from_common_root = path_dst.parts[index_common_root_name:]  # ('2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929', 'Dagster__Dagster', 'Dagster__DOCKER_COMPOSE', 'docker_compose', 'docker-compose.yml')
    context.log.debug(f"{rel_path_dst_from_common_root = }")

    path_src_up = "../" * len(rel_path_src_from_common_root)  # '../../../../'
    context.log.debug(f"{path_src_up = }")

    rel_path_from_src_to_dst_via_common_root = pathlib.Path(path_src_up, *rel_path_dst_from_common_root)  # PosixPath('../../../../2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929/Dagster__Dagster/Dagster__DOCKER_COMPOSE/docker_compose/docker-compose.yml')
    context.log.debug(f"{rel_path_from_src_to_dst_via_common_root = }")

    return rel_path_from_src_to_dst_via_common_root


def get_bool_env(
        env: str,
        default: bool = False,
):
    # os.getenv("VAR") always returns a string if VAR is set

    # EMPTY_VAR=
    # os.getenv("EMPTY_VAR", "some_value") returns value of EMPTY_VAR
    # whereas what we want is something like:
    # os.getenv("EMPTY_VAR") or "some_value"

    _env = os.getenv(env)

    if _env is None:
        _env = False
    elif _env.lower() == "true":
        _env = True
    elif _env.lower() == "false":
        _env = False
    else:
        _env = default

    return _env


def get_str_env(
        env: str,
        default: str,
):

    # EMPTY_VAR=
    # os.getenv("EMPTY_VAR", "some_value") returns value of EMPTY_VAR
    # whereas we want:
    # os.getenv("EMPTY_VAR") or "some_value"

    _env = os.getenv(env)

    if bool(_env):
        _env = env
    else:
        # bool("") evaluates to False, hence, set default
        # instead of returning empty string.
        _env = default

    return _env
