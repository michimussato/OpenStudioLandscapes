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
    "get_feature_config",
    "expand_dict_vars",
    "metadatavalues_from_dict",
    "get_relative_path_via_common_root",
    "get_bool_env",
    "get_str_env",
    "get_dynamic_ins",
    "get_image_metadata",
    "create_image",
    "get_networks_dict",
    "get_docker_compose_names",
    "download_file",
    "get_docker_run_cmd",
]

import copy
import datetime
import json
import os
import pathlib
import shlex
import time
from typing import Any, Dict, List, MutableMapping, Tuple, Union

import git
import requests
import yaml
from dagster import (
    AssetExecutionContext,
    MetadataValue,
    OpExecutionContext,
)

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine.config.models import DockerConfigModel
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.exceptions import (
    ComposeScopeException,
    OpenStudioLandscapesException,
)
from OpenStudioLandscapes.engine.logging.loggers import ENGINE_LOGGER as LOGGER
from OpenStudioLandscapes.engine.utils.docker import *


def cmd_list_to_str(
    cmd_list: List[str],
) -> str:
    cmd_str = " ".join(shlex.quote(s) for s in cmd_list)
    return cmd_str


def get_pip_install_str(
    pip_install_packages: List[str],
    python_str: str = "python{PYTHON_MAJ}.{PYTHON_MIN}",
    single_run_layer: bool = True,
    # Todo
    #  - [ ] enable `bust_cache` by default?
    bust_cache: bool = False,  # https://medium.com/@aleksej.gudkov/how-to-disable-cache-in-docker-build-a-complete-guide-372e20507ed9
) -> str:
    if bool(pip_install_packages):
        if single_run_layer:
            pip_install_str: str = (
                "RUN %s -m pip install --root-user-action=ignore %s"
                % (
                    python_str,
                    shlex.join(pip_install_packages),
                )
            )
            pip_install_str += " && %s -m pip cache purge" % (python_str)
            if bust_cache:
                pip_install_str += (
                    f" && echo \"Cache busted at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"\n"
                    # f" && echo \"Cache busted at $(date)\"\n"
                )
        else:
            pip_install_str: str = str()
            for pip_package in pip_install_packages:
                pip_install_str += (
                    "RUN %s -m pip install --root-user-action=ignore '%s'\n"
                    % (
                        python_str,
                        pip_package,
                    )
                )
            if bust_cache:
                # Resources:
                # - [How to Disable Cache in Docker Build: A Complete Guide](https://medium.com/@aleksej.gudkov/how-to-disable-cache-in-docker-build-a-complete-guide-372e20507ed9)
                # - [Latest code from Github (or similar) - use the Github API](https://stackoverflow.com/a/65762156)
                pip_install_str += (
                    f"RUN echo \"Cache busted at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"\n"
                    # f"RUN echo \"Cache busted at $(date)\"\n"
                )

        return pip_install_str

    else:
        return ""


def get_apt_install_str(
    apt_install_packages: List[str],
    single_run_layer: bool = True,
) -> str:
    if bool(apt_install_packages):
        if single_run_layer:
            # Use Single RUN layer for all packages
            # Ref: https://github.com/michimussato/OpenStudioLandscapes/issues/4
            apt_install_str: str = (
                f"RUN apt-get update && apt-get -y install --no-install-recommends {shlex.join(apt_install_packages)}"
            )
            apt_install_str += " && apt-get -y autoremove --purge"
            apt_install_str += " && apt-get -y clean"
            apt_install_str += " && apt-get -y autoclean"

        else:
            apt_install_str: str = str()
            for apt_package in apt_install_packages:
                apt_install_str += (
                    f"RUN apt-get install -y --no-install-recommends '{apt_package}'\n"
                )
        return apt_install_str

    else:
        return ""


def get_copy_str(
    temp_dir: pathlib.Path,
    copy_packages: Dict[str, pathlib.Path],
    mode: Union[int | None] = None,
) -> str:
    """
    Copies the files required for the build to
    the Dockerfile context so that they are actually
    accessible from within the context.

    Args:
        temp_dir: pathlib.Path
        copy_packages:
        mode:

    Returns:
        copy_str: str
    """
    # Todo:
    #  - [ ] COPY vs. ADD?
    copy_str: str = str()
    # --chmod is a buildx feature. Trying to avoid that because
    # buildx is causing problems if the registry is only reachable
    # by inscure HTTP
    # _mode = "" if mode is None else f"--chmod={str(mode).zfill(4)}"
    _mode = "" if mode is None else str(mode).zfill(4)
    for copy_package in copy_packages.keys():
        copy_str += f"COPY ./{temp_dir.name}/{copy_package} .\n"
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
    """Get the Git base path of a file which lives inside a repository."""
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
    context: AssetExecutionContext,
    docker_config: DockerConfigModel,
) -> str:

    image_path = []
    context.log.debug(f"{docker_config = }")
    context.log.debug(f"{type(docker_config) = }")

    if not isinstance(docker_config, DockerConfigModel):
        raise TypeError(
            "`docker_config` must be a DockerConfigModel. " f"{type(docker_config) = }"
        )

    image_on_localhost_only = not docker_config.use_registry

    # The idea is: explicit is better than implicit
    # In reality, we have to deal with 3 cases IF
    # images are named/tagged implicitly:
    # - local: <image_name>:<tag>
    # - registry:
    #   - docker.io: <repository>/<image_name>:<tag>
    #     (which is implicit for docker.io/<repository>/<image_name>:<tag>
    #   - arbitrary: <registry>/<repository>/<image_name>:<tag>
    # Let's just name/tag everything explicitly so that we only
    # have to deal with 3 cases:
    # - local
    # - registry
    # by ALWAYS prepending the <registry> part

    if image_on_localhost_only:
        # Never
        # - prefix a <registry>/<repository>
        # Hence, return empty string
        return str("")
    else:

        prepend_registry = docker_config.use_registry

        _repository_name = docker_config.docker_registry_config.docker_repository_name
        _docker_registry_url = docker_config.docker_registry_config.docker_registry_fqdn
        _repository_port = docker_config.docker_registry_config.docker_registry_port

        if bool(prepend_registry):
            if bool(_docker_registry_url):
                image_path.append(_docker_registry_url)

                if bool(_repository_port):
                    image_path.append(":")
                    image_path.append(str(_repository_port))

                image_path.append("/")

        if bool(_repository_name):
            image_path.append(_repository_name)
            image_path.append("/")

        return str().join(image_path)


def get_compose_scope(
    context: Union[
        OpExecutionContext, AssetExecutionContext
    ],  # Todo: necessary? -> Yes: `OpenStudioLandscapes.engine.base.ops.op_constants`
    features: MutableMapping,
    name: str,
) -> str:

    feature_keys = features.keys()

    LOGGER.info(f"{features = }")

    _module = name
    _parent = ".".join(_module.split(".")[:-1])
    context.log.info(f"{_parent = }")
    _definitions = ".".join([_parent, "definitions"])

    COMPOSE_SCOPE = None
    for key in feature_keys:
        if features[key]["module"] == _definitions:
            COMPOSE_SCOPE: str = features[key]["compose_scope"]
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

    # Todo:
    #  - [ ] make sure $PS1 is not causing errors

    for k, v in dict_to_expand.items():
        if isinstance(v, str):
            try:
                dict_to_expand[k] = v.format(**kv)
            except KeyError as e:
                raise OpenStudioLandscapesException(
                    f"Could not expand {dict_to_expand[k] = } in {dict_to_expand = }"
                ) from e
        elif isinstance(v, pathlib.PosixPath):
            try:
                dict_to_expand[k] = pathlib.PosixPath(v.as_posix().format(**kv))
            except KeyError as e:
                raise OpenStudioLandscapesException(
                    f"Could not expand {dict_to_expand[k] = } in {dict_to_expand = }"
                ) from e

    return dict_to_expand


# def serialize_dict(
#     context: Union[AssetExecutionContext, OpExecutionContext],
#     d: Dict,
#     d_: Dict = None,
# ) -> Dict:
#     if d_ is None:
#         d_ = {}
#
#     for k, v in d.items():
#
#         context.log.error(f"{k = }")
#         context.log.error(f"{type(v) = }")
#         context.log.error(f"{v = }")
#         if isinstance(v, Dict):
#             d_[k] = serialize_dict(
#                 context=context,
#                 d=v,
#                 d_=d_,
#             )
#         elif isinstance(v, BaseModel):
#             d_[k] = serialize_dict(
#                 context=context,
#                 d=json.loads(v.model_dump_json(indent=2, fallback=str)),
#                 d_=d_,
#             )
#             # d_dump = json.loads(v.model_dump_json(indent=2, fallback=str))
#             # if isinstance(d_dump, dict):
#             #     d_[k] = serialize_dict(
#             #         context=context,
#             #         d=d_dump,
#             #         d_=d_,
#             #     )
#             # else:
#             #     d_[k] = d_dump
#         elif isinstance(v, enum.Enum):
#             d_[k] = v.value
#         elif isinstance(v, pathlib.PosixPath):
#             d_[k] = v.as_posix()
#         else:
#             d_[k] = v
#
#     return d_


# Todo
#  - [ ] write a decent serializer
def metadatavalues_from_dict(
    context: Union[AssetExecutionContext, OpExecutionContext],
    d: Dict,
) -> Dict:

    d_serialized = json.loads(
        json.dumps(
            d,
            indent=2,
            default=str,
        )
    )

    metadata = {}

    metadata["OUT"] = MetadataValue.json(d_serialized)

    for k, v in d_serialized.items():
        context.log.debug(f"{type(v) = } ({v = })")
        metadata[k] = MetadataValue.json(v)
        # if isinstance(v, pathlib.PosixPath):
        #     metadata[k] = MetadataValue.path(v)
        # else:
        #     metadata[k] = MetadataValue.json(v)

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
    common_root_parts = (
        path_common_root.parts
    )  # ('/', 'opt', 'openstudiolandscapes', '.landscapes')

    # Todo
    #  - [ ] What if common_root_name occurs multiple times?
    if not common_root_parts.count(common_root_name) == 1:
        raise Exception(f"{common_root_name = } occurs multiple times.")
    index_common_root_name = common_root_parts.index(common_root_name)  # 3
    # We don't want .landscapes to be part of the path: increment index by 1
    index_common_root_name += 1  # 4
    context.log.debug(f"{index_common_root_name = }")

    rel_path_src_from_common_root = path_src.parent.parts[
        index_common_root_name:
    ]  # ('2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929', 'ComposeScope_default__ComposeScope_default', 'ComposeScope_default__DOCKER_COMPOSE', 'docker_compose')
    context.log.debug(f"{rel_path_src_from_common_root = }")
    rel_path_dst_from_common_root = path_dst.parts[
        index_common_root_name:
    ]  # ('2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929', 'Dagster__Dagster', 'Dagster__DOCKER_COMPOSE', 'docker_compose', 'docker-compose.yml')
    context.log.debug(f"{rel_path_dst_from_common_root = }")

    path_src_up = "../" * len(rel_path_src_from_common_root)  # '../../../../'
    context.log.debug(f"{path_src_up = }")

    rel_path_from_src_to_dst_via_common_root = pathlib.Path(
        path_src_up, *rel_path_dst_from_common_root
    )  # PosixPath('../../../../2025-06-06-00-40-48-0ef417aaff9d4da7a435412ae6f27929/Dagster__Dagster/Dagster__DOCKER_COMPOSE/docker_compose/docker-compose.yml')
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

    if env not in os.environ:
        return default

    _env = os.environ[env]
    if not bool(_env):
        LOGGER.warning(
            f"Environment variable {env = } is set but has empty value. "
            f"Setting value to {default = }"
        )
        _env = default

    return _env


def get_all_compose_scopes(
    usable_features: Dict[str, discovery.OpenStudioLandscapesDiscoveredFeature],
) -> set:
    compose_scopes = []

    package: str
    feature: discovery.OpenStudioLandscapesDiscoveredFeature
    for package, feature in usable_features.items():
        LOGGER.info(f"Usable {feature = }")
        compose_scopes.append(feature.config.compose_scope)
    return set(compose_scopes)


# Todo
#  - [ ] This function gets called multiple times:
#        - OpenStudioLandscapes.engine.compose_scopes.assets.feature_ins
#        - [removed] OpenStudioLandscapes.engine.compose_scopes.definitions.feature_ins
#        - OpenStudioLandscapes.engine.landscape_map.assets.feature_ins
#        - [removed] OpenStudioLandscapes.engine.landscape_map.definitions.feature_ins
def get_dynamic_ins(
    imported_features: Dict,
):
    """
    Dynamic inputs based on the imported
    third party code locations

    Args:
        imported_features:

    Returns:

    """

    feature_ins = {}

    package: str
    feature: discovery.OpenStudioLandscapesDiscoveredFeature
    feature_names: List[str] = []
    for feature in imported_features.values():
        if not feature.config.enabled:
            feature_names.append(feature.config.feature_name)
    for package, feature in imported_features.items():
        LOGGER.debug(f"{feature = }")
        # feature = OpenStudioLandscapesDiscoveredFeature(definitions='OpenStudioLandscapes.Watchtower.definitions', definitions_object=<module 'OpenStudioLandscapes.Watchtower.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Watchtower/src/OpenStudioLandscapes/Watchtower/definitions.py'>, models='OpenStudioLandscapes.Watchtower.config.models', models_object=<module 'OpenStudioLandscapes.Watchtower.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Watchtower/src/OpenStudioLandscapes/Watchtower/config/models.py'>, config=Feature(['env=None', "config_engine=openstudiolandscapes__docker_config=DockerConfigModel(use_registry=True, no_cache=False, docker_registry_config=DockerRegistryConfig(docker_push=True, docker_pull=True, docker_repository_name='openstudiolandscapes', docker_registry_access='public', docker_registry_protocol='https', docker_registry_fqdn='registry.openstudiolandscapes.lan', docker_registry_port=5000, docker_registry_username='registry-user', docker_registry_password='registry-password')) openstudiolandscapes__repository_root=PosixPath('{REPOSITORY_ROOT}') openstudiolandscapes__domain_lan='openstudiolandscapes.lan'", 'config_parent=None', 'distribution=<importlib.metadata.PathDistribution object at 0x7fe9b764ad10>', 'enabled=True', 'compose_scope=default', 'feature_name=OpenStudioLandscapes-Watchtower', 'group_name=watchtower', "key_prefixes=['Watchtower']", 'docker_compose={DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml', 'definitions=OpenStudioLandscapes.Watchtower.definitions', 'watchtower_port_host=4000', 'watchtower_port_container=80']))

        feature_enabled: bool = feature.config.enabled

        feature_name = feature.config.feature_name
        compose_scope = feature.config.compose_scope
        group_name = feature.config.group_name
        key_prefixes = feature.config.key_prefixes

        # Skip Feature if disabled in `config.yml`
        if not feature_enabled:
            # Todo
            #  - [ ] We get duplicate log messages here
            LOGGER.info(f"Feature [{feature_name.ljust(max([len(i) for i in feature_names]))}] "
                        f"is installed but DISABLED in {feature.config.config_file_path.as_posix()}")
            continue

        asset_in = feature.config.dagster_compose_scope_in

        if compose_scope not in feature_ins:
            feature_ins[compose_scope]: Dict = {}

        feature_ins[compose_scope][group_name] = asset_in

        LOGGER.debug(f"{feature_ins[compose_scope][group_name] = }")

    # feature_ins = {'default': {'OpenStudioLandscapes_Kitsu': AssetIn(key=AssetKey(['Kitsu', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_Watchtower': AssetIn(key=AssetKey(['Watchtower', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}, 'test': {'OpenStudioLandscapes_VERT': AssetIn(key=AssetKey(['VERT', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}}
    return feature_ins


def get_image_metadata(
    context: AssetExecutionContext,
    docker_image: dict,
    docker_config: DockerConfigModel,
    env,
):

    build_base_image_data: dict = docker_image
    context.log.debug(f"{build_base_image_data = }")
    # build_base_image_data = {'image_name': 'openstudiolandscapes_base_build_docker_image', 'image_prefixes': '', 'image_tags': ['2025-11-17-01-26-31-05a9b85aa33b47ffa7dfb21a28ca24ab'], 'image_parent': {}}

    build_base_docker_config: DockerConfigModel = docker_config
    context.log.debug(f"{build_base_docker_config = }")
    # build_base_docker_config = build_base_docker_config = <DockerConfig.LOCALHOST: {'docker_registry_url': <DockerRegistry.LOCAL_LOCALHOST: 'localhost'>, 'docker_registry_port': None, 'docker_registry_username': None, 'docker_registry_password': None, 'docker_repository_type': <DockerRepositoryType.PUBLIC: 'public'>}>

    build_base_parent_image_prefix: str = build_base_image_data["image_prefixes"]

    build_base_parent_image_name: str = build_base_image_data["image_name"]

    build_base_parent_image_tags: list = build_base_image_data["image_tags"]

    image_name = get_image_name(context=context)

    image_prefixes = parse_docker_image_path(
        context=context,
        docker_config=build_base_docker_config,  # DockerRegistryConfig
    )

    tags = [
        env.get("LANDSCAPE", str(time.time())),
    ]

    context.log.debug(f"{image_name = }")
    # image_name = 'nukerlm_8_build_docker_image'
    context.log.debug(f"{image_prefixes = }")
    # image_prefixes = ''
    context.log.debug(f"{tags = }")
    # tags = ['2025-11-17-01-26-31-05a9b85aa33b47ffa7dfb21a28ca24ab']
    context.log.debug(f"{build_base_parent_image_prefix = }")
    # build_base_parent_image_prefix = ''
    context.log.debug(f"{build_base_parent_image_name = }")
    # build_base_parent_image_name = 'openstudiolandscapes_base_build_docker_image'
    context.log.debug(f"{build_base_parent_image_tags = }")
    # build_base_parent_image_tags = ['2025-11-17-01-26-31-05a9b85aa33b47ffa7dfb21a28ca24ab']

    return (
        image_name,
        image_prefixes,
        tags,
        build_base_parent_image_prefix,
        build_base_parent_image_name,
        build_base_parent_image_tags,
    )


def create_image(
    context: AssetExecutionContext,
    image_name,
    image_prefixes,
    tags,
    docker_image: Dict,
    docker_config: DockerConfigModel,
    docker_config_json: pathlib.Path,
    docker_file: pathlib.Path,
    build_context: Union[None, pathlib.Path] = None,
):

    image_data = {
        "image_name": image_name,
        "image_prefixes": image_prefixes,
        "image_tags": tags,
        "image_parent": copy.deepcopy(docker_image),
    }

    cmds = []

    tags_full_str = [f"{image_prefixes}{image_name}:{tag}" for tag in tags]
    context.log.debug(f"{tags_full_str = }")

    localhost_only = not docker_config.use_registry
    # Todo:
    #  - [ ] if localhost_only is True, the images will
    #        get tagged with docker.io/library/ automatically
    #        Is this expected?
    #        [...]
    #        "stderr: #11 naming to docker.io/library/openstudiolandscapes_kitsu_build_docker_image:2026-02-25_12-05-59__spark-dear-square-axolotl done",
    #        [...]

    if localhost_only:
        pull = False
        push = False
    else:
        pull = docker_config.docker_registry_config.docker_pull
        push = docker_config.docker_registry_config.docker_push

    context.log.debug(f"{localhost_only = }")

    cmd_build = docker_build_cmd(
        context=context,
        docker_config_json=docker_config_json,
        docker_file=docker_file,
        tags=tags_full_str,
        pull=pull,
        no_cache=docker_config.no_cache,
        build_context=build_context,
    )

    cmds.append(cmd_build)

    if push:
        cmds_push = docker_push_cmd(
            context=context,
            docker_config_json=docker_config_json,
            tags_full=tags_full_str,
        )

        cmds.extend(cmds_push)
    else:
        pass

    context.log.info(f"{cmds = }")

    logs = docker_do(
        context=context,
        cmds=cmds,
    )

    context.log.debug(f"{image_data = }")
    context.log.debug(f"{logs = }")

    return image_data, logs


def get_networks_dict(
    context: Union[AssetExecutionContext, OpExecutionContext],
    compose_file: pathlib.Path,
) -> Dict:
    """
    Analyze compose_file for `networks` and return a nested dict of networks
    if networks exist, otherwise return empty dict.

    Args:
        context: AssetExecutionContext
        compose_file: pathlib.Path

    Returns:
        networks: dict
    """
    with open(compose_file, "r") as fr:
        compose_dict = yaml.load(fr, Loader=yaml.FullLoader)
        context.log.debug(f"{compose_dict = }")
        networks = compose_dict.get("networks", {})
        context.log.debug(f"{networks = }")

    return networks


def get_docker_compose_names(
    context: Union[AssetExecutionContext, OpExecutionContext],
    service_name: str,
    landscape_id: str,
    domain_lan: str,
) -> Tuple[str, str]:
    """
    Takes the service name and returns container_name and
    host_name based on that.

    Args:
        context: Union[dagster.AssetExecutionContext, dagster.OpExecutionContext]
        service_name: str
        landscape_id: str
        domain_lan: str

    Returns:
        container_name: str
        host_name: str

    """
    # Todo
    #  - [ ] Implement check so that none of the given strings
    #        and the results do not exceed 63 chars (6 bits)
    #        per segment.
    #        https://github.com/michimussato/OpenStudioLandscapes/issues/48

    container_name = ".".join([service_name, landscape_id])
    host_name = ".".join([service_name, domain_lan])
    return container_name, host_name


def download_file(
    url: str,
    dest_folder: pathlib.Path,
) -> pathlib.Path:
    if not dest_folder.exists():
        dest_folder.mkdir(
            parents=True, exist_ok=True
        )  # create folder if it does not exist

    filename = url.split("/")[-1].replace(" ", "_")  # be careful with file names
    file_path = dest_folder / filename

    r = requests.get(url, stream=True)
    if r.ok:
        LOGGER.info("Saving to %s" % file_path.absolute().as_posix())
        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        return file_path
    else:  # HTTP status code 4XX/5XX
        raise Exception(
            "Download failed: status code {}\n{}".format(r.status_code, r.text)
        )


def get_docker_run_cmd(
    image_data: Dict,
    context: Union[AssetExecutionContext, OpExecutionContext],
) -> str:

    context.log.debug(f"{image_data = }")

    def _get_cmd() -> List[str]:
        cmd = [
            "docker",
            "run",
            "--interactive",
            "--tty",
            "--rm",
            "--entrypoint",
            "bash",
        ]

        context.log.debug(f"{cmd = }")

        return cmd

    ret = shlex.join(
        [
            *_get_cmd(),
            f"{image_data['image_prefixes']}{image_data['image_name']}:{image_data['image_tags'][0]}",
        ]
    )

    context.log.debug(f"{ret = }")

    return ret
