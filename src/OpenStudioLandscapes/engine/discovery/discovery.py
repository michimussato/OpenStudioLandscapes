"""
This is the Feature discovery engine for OpenStudioLandscapes.
It's a bit messy in here for two reasons -
1. The project has grown with this as an underlying core feature
2. I couldn't come up with a better solution yet

Things that could be improved
- config.yaml to allow for comments
  - Currently, the files are read and dumped again,
    removing all comments whatsoever
    - Migration to `ruamel.yaml` might be an option
      - https://www.w3reference.com/blog/python-yaml-update-preserving-order-and-comments/#why-preserving-order-and-comments-matters
      - https://stackoverflow.com/questions/55253090/how-to-round-trip-ruamel-yaml-strings-like-on
  - This mechanism, however, allows to dynamically
    add/remove YAML key/value pairs based on the underlying
    model.
- avoid re-discovery at runtime whenever possible and if
  not explicitly asked for
  Requirements:
  - cache has to persist across processes
    - Redis? https://www.youtube.com/watch?v=mHJoq4aK4lk
  - invalidation of cache has to happen on Reload definitions
- maybe migrate to a pure Code Location approach at some point
- discovery does more than it's supposed to be doing
  - Repo initialization
    - init_config_store()


The logic currently does:
- not add documenting comments to the initial YAML files
- add new keys from model fields to the YAML
- not remove keys from the YAML of non-existing model fields
- keep comments in the YAML files
  - [How to Update YAML in Python While Preserving Order and Comments: A Step-by-Step Guide](https://www.w3reference.com/blog/python-yaml-update-preserving-order-and-comments/)
"""

import importlib
import json
import os
import pathlib
from collections import OrderedDict
from importlib import metadata
from importlib.metadata import Distribution
from types import ModuleType
from typing import Dict, List, Tuple, Union

import ruamel.yaml
from pydantic_core._pydantic_core import ValidationError as PydanticValidationError
from setuptools import find_namespace_packages

from OpenStudioLandscapes.engine import dist as dist_engine
from OpenStudioLandscapes.engine.config.models import (
    ConfigEngine,
    FeatureBaseModel,
    OpenStudioLandscapesDiscoveredFeature,
)
from OpenStudioLandscapes.engine.discovery.init_config_store import (
    commit_configs,
    init_config_store,
)
from OpenStudioLandscapes.engine.logging.loggers import DISCOVERY_LOGGER as LOGGER


class OpenStudioLandscapesDiscoveryException(Exception):
    pass


def get_verified_config(
    config_file: pathlib.Path,
) -> ruamel.yaml.CommentedMap:

    data: ruamel.yaml.CommentedMap = load_yaml(
        file_path=config_file,
    )

    msg = f"config.yml contains no data: {config_file.as_posix()}"
    assert bool(data), msg
    # This "should not" happen but
    # due to a previous bug that lead to
    # exaclty that, this acts as a "safety net".
    return data


# Todo
#  - [ ] more specific return type
def get_dynamic_ins(
    imported_features: Dict,
) -> Dict:
    """
    Dynamic inputs based on the imported
    third party code locations

    Args:
        imported_features:

    Returns:

    """

    feature_ins = {}

    package: str
    feature: OpenStudioLandscapesDiscoveredFeature
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
            LOGGER.info(
                f"Feature [{feature_name.ljust(max([len(i) for i in feature_names]))}] "
                f"is installed but DISABLED in {feature.config.config_file_path.as_posix()}"
            )
            continue

        asset_in = feature.config.dagster_compose_scope_in

        if compose_scope not in feature_ins:
            feature_ins[compose_scope]: Dict = {}

        feature_ins[compose_scope][group_name] = asset_in

        LOGGER.debug(f"{feature_ins[compose_scope][group_name] = }")

    # feature_ins = {'default': {'OpenStudioLandscapes_Kitsu': AssetIn(key=AssetKey(['Kitsu', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>), 'OpenStudioLandscapes_Watchtower': AssetIn(key=AssetKey(['Watchtower', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}, 'test': {'OpenStudioLandscapes_VERT': AssetIn(key=AssetKey(['VERT', 'feature_out']), metadata=None, key_prefix=[], input_manager_key=None, partition_mapping=None, dagster_type=<class 'dagster._core.definitions.utils.NoValueSentinel'>)}}
    return feature_ins


LOGGER.info("Start bootstrapping...")


# https://www.w3reference.com/blog/python-yaml-update-preserving-order-and-comments/#why-preserving-order-and-comments-matters
def load_yaml(
    file_path: pathlib.Path,
) -> ruamel.yaml.CommentedMap:
    """Load a YAML file and return its data (preserving comments/order)."""
    yaml_ = ruamel.yaml.YAML(typ="rt")  # 'rt' = round-trip mode
    yaml_.preserve_quotes = True  # Keep string quotes (e.g., "MyApp" vs MyApp)
    with open(file_path, "r") as fr:
        data: ruamel.yaml.CommentedMap = yaml_.load(fr)

    LOGGER.debug(f"Loaded data from config.yml: {data}")

    if data is None:
        raise OpenStudioLandscapesDiscoveryException(
            "Could not load YAML file: \n" f"{file_path = }\n" f"{data = }\n"
        )

    return data


def dump_yaml(
    model_config: Union[ConfigEngine, FeatureBaseModel],
    file_path: pathlib.Path,
) -> None:
    """Save YAML data to a file, preserving comments/order."""

    # if file_path.exists() is not necessary - part of get_config()
    # So, the config.yml file exists at this point (WRONG). However,
    # it also has to be populated with data. If it is an empty
    # file or a non-empty file with an empty dict, populate
    # default data.

    current_config_: ruamel.yaml.CommentedMap = get_config(
        file_path_config_yaml=file_path,
    )
    LOGGER.debug(f"{current_config_ = }")

    model_dump_json: str = model_config.model_dump_json(
        indent=2,
        fallback=str,
    )
    model_dump_dict: Dict = json.loads(model_dump_json)

    if file_path.exists():
        # If the file already exists, don't touch
        # it for the time being.
        # Just analyze it and find differences
        # between the keys in the file and
        # keys in the model.
        #
        # Todo:
        #  - [ ] Develop some logic so that
        #        the existing file does not get
        #        overwritten just like that.
        #        Keeping control over file handle
        #        concurrency with Dagster is not straight
        #        forward it seems.
        #        Of course, we need to make sure that
        #        new/changed model fields don't result
        #        in non-functional situations.
        #        - "Migration" logic?

        data: ruamel.yaml.CommentedMap = get_verified_config(
            config_file=file_path,
        )

        LOGGER.debug(f"{data = }")
        # data = {'HKEY_BIN': '{DOT_FEATURES}/{FEATURE}/.payload/bin/hkey-bin', 'HSERVER': '{DOT_FEATURES}/{FEATURE}/.payload/bin/hserver', 'LICENSES': '{DOT_FEATURES}/{FEATURE}/.payload/bin/licenses', 'LICENSES_ACTIVE': '{DOT_FEATURES}/{FEATURE}/.payload/data/licenses', 'LICENSES_DISABLED': '{DOT_FEATURES}/{FEATURE}/.payload/bin/licenses.disabled', 'SESICTRL': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesictrl', 'SESINETD': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd', 'SESINETD_PEAK_USAGE_BIN': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd_peak_usage.bin', 'SESIUSAGE': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesiusage', 'SESI_PORT_CONTAINER': 1715, 'SESI_PORT_HOST': 1717, 'apt_packages': ['lsb-release'], 'compose_scope': 'license_server', 'docker_compose': '{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml', 'enabled': True, 'env': {}, 'feature_name': 'OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20', 'group_name': 'OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20', 'key_prefixes': ['OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20'], 'local_bind_volumes': [], 'local_environment_variables': {}}

        keys_expected = model_dump_dict.keys()
        LOGGER.debug(f"{keys_expected = }")
        # keys_expected = dict_keys(['env', 'local_bind_volumes', 'local_environment_variables', 'group_name', 'key_prefixes', 'enabled', 'compose_scope', 'feature_name', 'docker_compose', 'LICENSES_ACTIVE', 'HKEY_BIN', 'HSERVER', 'LICENSES', 'LICENSES_DISABLED', 'SESICTRL', 'SESINETD', 'SESINETD_PEAK_USAGE_BIN', 'SESIUSAGE', 'SESI_PORT_HOST', 'SESI_PORT_CONTAINER', 'apt_packages'])

        # current_config_.keys()
        keys_actual = dict(current_config_).keys()
        LOGGER.debug(f"{keys_actual = }")
        # keys_actual = dict_keys(['HKEY_BIN', 'HSERVER', 'LICENSES', 'LICENSES_ACTIVE', 'LICENSES_DISABLED', 'SESICTRL', 'SESINETD', 'SESINETD_PEAK_USAGE_BIN', 'SESIUSAGE', 'SESI_PORT_CONTAINER', 'SESI_PORT_HOST', 'apt_packages', 'compose_scope', 'docker_compose', 'enabled', 'env', 'feature_name', 'group_name', 'key_prefixes', 'local_bind_volumes', 'local_environment_variables'])

        if keys_expected != keys_actual:

            LOGGER.critical("Model keys and `config.yml` keys differ.")

            missing_keys = set(keys_expected) - set(keys_actual)
            unused_keys = set(keys_actual) - set(keys_expected)
            LOGGER.debug(f"{missing_keys = }")
            LOGGER.debug(f"{unused_keys = }")

            # IMPORTANT
            # We don't want to edit a config.yml file automatically.
            # This can have unwanted side effects and takes away control
            # from the user. Just highlight the problem (or raise
            # an exception) here.

            if bool(missing_keys):
                # Todo:
                #  - [ ] This is not very graceful, so, maybe we
                #        can come up with a better solution when
                #        keys are missing.
                msg = (
                    f"config.yml has missing keys. Please manually "
                    f"add {missing_keys} to {file_path.as_posix()} "
                    f"or delete {file_path.as_posix()} to have it "
                    f"automatically re-generated with default values. "
                    f"We cannot continue gracefully. You can, however, fix the "
                    f"problem and `Reload Definitions` without "
                    f"restarting OpenStudioLandscapes."
                )
                LOGGER.critical(msg)
                # This is currently dealt with by `except PydanticValidationError as e:`
                raise OpenStudioLandscapesDiscoveryException(msg)

            if bool(unused_keys):
                # This is not critical. It's just not
                # clean to have unused keys in the config.yml.
                LOGGER.warning(
                    f"Unused keys found in YAML file. Please manually "
                    f"remove {unused_keys} from {file_path.as_posix()}."
                )

        LOGGER.info(f"Existing config.yml left untouched: {file_path.as_posix()}")

    else:
        # If the config.yml file does not exist,
        # here's where it will get created and
        # populated with default data
        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        yaml_ = ruamel.yaml.YAML(typ="rt")
        yaml_.indent(
            mapping=2,
            sequence=2,
            offset=0,
        )  # Match original indentation

        with open(file_path, "w") as f:
            yaml_.dump(model_dump_dict, f)

        LOGGER.info(f"config.yml successfully written: {file_path.as_posix()}")

    return None


def get_config(
    file_path_config_yaml: pathlib.Path,
) -> ruamel.yaml.CommentedMap:
    """
    Load YAML data to a file (if it exists), preserving comments/order,
    otherwise create an empty dict (ruamel.yaml.CommentedMap), and return it.
    Args:
        file_path_config_yaml:

    Returns:
        data: ruamel.yaml.CommentedMap
    """

    if file_path_config_yaml.exists():
        LOGGER.debug(f"config.yml found: {file_path_config_yaml.as_posix()}")

        data: ruamel.yaml.CommentedMap = get_verified_config(
            config_file=file_path_config_yaml,
        )

        LOGGER.debug(f"Returning data from file: {data}")
    else:
        LOGGER.debug(f"config.yml does not exist: {file_path_config_yaml.as_posix()}")
        # CommentedMap needs an OrderedDict.
        # Standard dict does not work.
        # Just return an empty CommentedMap to indicate that we're dealing
        # with non-existing configs.
        data: ruamel.yaml.CommentedMap = ruamel.yaml.CommentedMap(OrderedDict())
        LOGGER.debug(f"Returning empty data: {data}")

    return data


def get_absolute_config_path(
    dist: Distribution,
) -> pathlib.Path:
    """
    Get the absolute path of the configuration file. The
    file itself does not necessarily exist. This is just
    where it has to live.

    Returns:
        engine_config_path: pathlib.Path
    """

    LOGGER.debug(f"{dist.name = }")
    config_yml: pathlib.Path = OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.joinpath(
        dist.name,
        "config.yml",
    )
    config_yml_expanded: pathlib.Path = config_yml.expanduser()
    LOGGER.debug(f"{config_yml = }")
    LOGGER.info(f"{config_yml_expanded = }")
    return config_yml_expanded


# Important
# The Feature Git repositories have to physically exist locally.
# It's not enough to just pip install them from the repo directly, like:
# `pip install OpenStudioLandscapes-Ayon@git+https://github.com/michimussato/OpenStudioLandscapes-Ayon`
# Maybe one day...


# Get the openstudiolandscapes__configstore_root
# Todo
#  - [ ] fix circular import:
#        - `OpenStudioLandscapes.engine.config.models.FeatureBaseModel.config_file_path`
OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get(
        "OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
        # Todo:
        #  - [ ] if we launch OpenStudioLandscapes via `dagster dev`,
        #        this env var has not been set and will result in None -
        #        this is problematic. This is a workaround for now.
        #        -> see `dot_landscapes` asset for a better solution
        default="~/.config/OpenStudioLandscapes/config-store",
    )
).expanduser()
OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS: pathlib.Path = pathlib.Path(
    os.environ.get(
        "OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS",
        # Todo:
        #  - [ ] if we launch OpenStudioLandscapes via `dagster dev`,
        #        this env var has not been set and will result in None -
        #        this is problematic. This is a workaround for now.
        #        -> see `dot_landscapes` asset for a better solution
        default="~/.config/OpenStudioLandscapes/config-store",
    )
).expanduser()
# OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT: pathlib.Path = pathlib.Path(
#     os.environ.get(
#         "OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT",
#         # Todo:
#         #  - [ ] if we launch OpenStudioLandscapes via `dagster dev`,
#         #        this env var has not been set and will result in None -
#         #        this is problematic. This is a workaround for now.
#         default="~/.local/share/OpenStudioLandscapes",
#     )
# ).expanduser()


if not OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.expanduser().exists():
    OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.expanduser().mkdir(
        parents=True,
        exist_ok=False,
    )
    LOGGER.info(
        f"Repo dir created: {OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.expanduser().as_posix()}."
    )

config_store_repo, fresh_repo = init_config_store(
    root=OPENSTUDIOLANDSCAPES__CONFIGSTORE_VCS or OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT
)


def get_config_engine() -> ConfigEngine:
    """
    Get the Engine Configuration Model Object.
    This is a Singleton, so re-instantiating basically
    returns the already existing ConfigEngine object.

    Returns:
        ConfigEngine
    """

    engine_config_yml_expanded: pathlib.Path = get_absolute_config_path(
        dist=dist_engine,
    )

    engine_config_dict: ruamel.yaml.CommentedMap = get_config(
        file_path_config_yaml=engine_config_yml_expanded,
    )

    config_engine: ConfigEngine = ConfigEngine(
        **engine_config_dict,
    )
    LOGGER.debug(f"{config_engine = }")

    dump_yaml(
        model_config=config_engine,
        file_path=engine_config_yml_expanded,
    )

    return config_engine


def get_namespace_packages(
    where: pathlib.Path,
) -> List[str]:
    LOGGER.info(
        "Getting installed OpenStudioLandscapes namespace packages from '%s'...", where
    )

    namespace_packages_: List[str] = find_namespace_packages(
        where=where,
        include=["*src.OpenStudioLandscapes.*"],
        exclude=[
            "*.config",  # exclude src.OpenStudioLandscapes.<Feature>.config from module discovery (Todo: although I'm not yet sure if this must be excluded. Test!)
            "*.doc",  # exclude src.OpenStudioLandscapes.<Feature>.doc from module discovery
        ],
    )
    LOGGER.debug(f"{namespace_packages_ = }")
    # ['OpenStudioLandscapes-NukeRLM-8.src.OpenStudioLandscapes.NukeRLM_8', ...]

    # Just take the final part of the namespace package ('NukeRLM_8') an
    # prepend 'OpenStudioLandscapes'
    namespace_packages = [
        f"OpenStudioLandscapes.{i.split('.')[-1]}" for i in namespace_packages_
    ]

    LOGGER.info(f"{namespace_packages = }")
    # ['OpenStudioLandscapes.NukeRLM_8', ...]
    return namespace_packages


def get_definitions_path(namespace_package) -> str:
    LOGGER.info(
        "Converting namespace package path to definitions path: '%s'...",
        namespace_package,
    )
    definitions_path = ".".join(
        [
            namespace_package.rsplit(".", 2)[-2],
            namespace_package.rsplit(".", 2)[-1],
            "definitions",
        ]
    )
    LOGGER.info("Resulting definitions path: '%s'", definitions_path)
    return definitions_path


def get_models_path(namespace_package) -> str:
    LOGGER.info(
        "Converting namespace package path to models path: '%s'...", namespace_package
    )
    definitions_path = ".".join(
        [
            namespace_package.rsplit(".", 2)[-2],
            namespace_package.rsplit(".", 2)[-1],
            "config",
            "models",
        ]
    )
    LOGGER.info("Resulting models path: '%s'", definitions_path)
    return definitions_path


def try_import_discovered(
    package: str,
    discovered_model: OpenStudioLandscapesDiscoveredFeature,
) -> Tuple[ModuleType, ModuleType]:
    """Try to import a discovered model from a package."""

    LOGGER.info(f"{package = }")
    LOGGER.debug(f"{discovered_model = }")
    try:
        _models = discovered_model.models
        LOGGER.debug(f"{_models = }")
        models_object: ModuleType = importlib.import_module(_models)
        LOGGER.info("Feature models import successful: '%s'" % models_object)
    except (
        ModuleNotFoundError,
        AttributeError,
        # TypeError,
    ) as e:
        raise ImportError(e) from e
    try:
        _definitions = discovered_model.definitions
        LOGGER.debug(f"{_definitions = }")
        definitions_object: ModuleType = importlib.import_module(_definitions)
        LOGGER.info("Feature definitions import successful: '%s'" % definitions_object)
    except (
        ModuleNotFoundError,
        AttributeError,
        # TypeError,
    ) as e:
        raise ImportError(e) from e

    return models_object, definitions_object


def init(
    config_engine: ConfigEngine,
    discovered_models: Dict[str, OpenStudioLandscapesDiscoveredFeature],
) -> None:
    """
    Fill the discovered_models dictionary with the discovered models.
    (Does not return anything but edits the dict instead.)

    Args:
        config_engine:
        discovered_models:

    Returns:
        None
    """

    package: str

    for package in get_namespace_packages(
        where=pathlib.Path.cwd().joinpath(".features"),
    ):
        LOGGER.debug(f"{package = }")
        # package = 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20'

        feature_dict = {
            "definitions": get_definitions_path(package),
            "models": get_models_path(package),
        }
        module: OpenStudioLandscapesDiscoveredFeature = (
            OpenStudioLandscapesDiscoveredFeature(**feature_dict)
        )
        LOGGER.debug(f"{module = }")
        # module = OpenStudioLandscapesDiscoveredFeature(
        #     definitions='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions',
        #     definitions_object=None,
        #     models='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models',
        #     models_object=None,
        #     config=None,
        # )

        try:
            models_object, definitions_object = try_import_discovered(
                package=package,
                discovered_model=module,
            )
        except ImportError as e:
            LOGGER.exception(e)
            LOGGER.error("Feature import failed and won't be available: '%s'" % package)
            continue

        module.definitions_object = definitions_object
        LOGGER.debug(f"{module.definitions_object = }")
        # module.definitions_object = <module 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/src/OpenStudioLandscapes/SESI_gcc_9_3_Houdini_20/definitions.py'>

        module.models_object = models_object
        LOGGER.debug(f"{module.models_object = }")
        # module.models_object = <module 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/src/OpenStudioLandscapes/SESI_gcc_9_3_Houdini_20/config/models.py'>

        discovered_models[package] = module

    LOGGER.debug(f"{discovered_models = }")
    # discovered_models = {
    #     [...]
    #     'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20': (
    #         OpenStudioLandscapesDiscoveredFeature(
    #             definitions='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions',
    #             definitions_object=<module 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/src/OpenStudioLandscapes/SESI_gcc_9_3_Houdini_20/definitions.py'>,
    #             models='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models',
    #             models_object=<module 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/src/OpenStudioLandscapes/SESI_gcc_9_3_Houdini_20/config/models.py'>,
    #             config=None,
    #         ),
    #     ),
    #     [...]
    # }

    # Annotate the types before the loop
    # References:
    # - https://stackoverflow.com/a/41641489/2207196
    package: str
    feature: OpenStudioLandscapesDiscoveredFeature
    for package, feature in discovered_models.items():
        LOGGER.debug(f"{package = }")
        # package = 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20'
        LOGGER.debug(f"{feature = }")
        # feature = OpenStudioLandscapesDiscoveredFeature(
        #     definitions='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions',
        #     definitions_object=<module 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/src/OpenStudioLandscapes/SESI_gcc_9_3_Houdini_20/definitions.py'>,
        #     models='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models',
        #     models_object=<module 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/src/OpenStudioLandscapes/SESI_gcc_9_3_Houdini_20/config/models.py'>,
        #     config=None,
        # )

        feature_dist: Distribution = metadata.distribution(package)
        LOGGER.debug(f"{feature_dist = }")
        # feature_dist = <importlib.metadata.PathDistribution object at 0x7fe647853dd0>

        config_yml_feature_expanded: pathlib.Path = get_absolute_config_path(
            dist=feature_dist,
        )
        LOGGER.debug(f"{config_yml_feature_expanded = }")
        # config_yml_feature_expanded = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/config.yml')

        feature_config_dict: ruamel.yaml.CommentedMap = get_config(
            file_path_config_yaml=config_yml_feature_expanded,
        )
        LOGGER.debug(f"{feature_config_dict = }")
        # feature_config_dict = {
        #     'HKEY_BIN': '{DOT_FEATURES}/{FEATURE}/.payload/bin/hkey-bin',
        #     'HSERVER': '{DOT_FEATURES}/{FEATURE}/.payload/bin/hserver',
        #     'LICENSES': '{DOT_FEATURES}/{FEATURE}/.payload/bin/licenses',
        #     'LICENSES_ACTIVE': '{DOT_FEATURES}/{FEATURE}/.payload/data/licenses',
        #     'LICENSES_DISABLED': '{DOT_FEATURES}/{FEATURE}/.payload/bin/licenses.disabled',
        #     'SESICTRL': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesictrl',
        #     'SESINETD': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd',
        #     'SESINETD_PEAK_USAGE_BIN': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd_peak_usage.bin',
        #     'SESIUSAGE': '{DOT_FEATURES}/{FEATURE}/.payload/bin/sesiusage',
        #     'SESI_PORT_CONTAINER': 1715,
        #     'SESI_PORT_HOST': 1717,
        #     'apt_packages': ['lsb-release'],
        #     'compose_scope': 'license_server',
        #     'docker_compose': '{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml',
        #     'enabled': True,
        #     'env': {},
        #     'feature_name': 'OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20',
        #     'group_name': 'OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20',
        #     'key_prefixes': ['OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20'],
        #     'local_bind_volumes': [],
        #     'local_environment_variables': {}
        # }
        try:
            config_feature: FeatureBaseModel = feature.models_object.Config(
                **feature_config_dict,
            )
            LOGGER.debug(f"{config_feature = }")
            #  config_feature = Feature(
            #      [
            #          'env={}',
            #          'local_bind_volumes=[]',
            #          'local_environment_variables={}',
            #          'config_engine=None',
            #          'distribution=None',
            #          'group_name=OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20',
            #          "key_prefixes=['OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20']",
            #          'enabled=True',
            #          'compose_scope=license_server',
            #          'feature_name=OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20',
            #          'docker_compose={DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml',
            #          'LICENSES_ACTIVE={DOT_FEATURES}/{FEATURE}/.payload/data/licenses',
            #          'HKEY_BIN={DOT_FEATURES}/{FEATURE}/.payload/bin/hkey-bin',
            #          'HSERVER={DOT_FEATURES}/{FEATURE}/.payload/bin/hserver',
            #          'LICENSES={DOT_FEATURES}/{FEATURE}/.payload/bin/licenses',
            #          'LICENSES_DISABLED={DOT_FEATURES}/{FEATURE}/.payload/bin/licenses.disabled',
            #          'SESICTRL={DOT_FEATURES}/{FEATURE}/.payload/bin/sesictrl',
            #          'SESINETD={DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd',
            #          'SESINETD_PEAK_USAGE_BIN={DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd_peak_usage.bin',
            #          'SESIUSAGE={DOT_FEATURES}/{FEATURE}/.payload/bin/sesiusage',
            #          'SESI_PORT_HOST=1717',
            #          'SESI_PORT_CONTAINER=1715',
            #          "apt_packages=['lsb-release']"
            #      ]
            #  )
        except PydanticValidationError as e:
            # We don't want to edit a config.yml file automatically.
            # This can have unwanted side effects and takes away control
            # from the user. Just raise an Exception and highlight the problem here.
            msg = f"`config.yml` needs to be updated with the following missing fields: {e}"
            LOGGER.error(msg)
            raise OpenStudioLandscapesDiscoveryException(msg)

        # Also inject the ConfigEngine object
        config_feature.config_engine = config_engine
        LOGGER.debug(f"{config_feature.config_engine = }")
        # config_feature.config_engine = ConfigEngine(openstudiolandscapes__docker_config=DockerConfigModel(use_registry=True, no_cache=False, docker_registry_config=DockerRegistryConfig(docker_push=True, docker_pull=True, docker_repository_name='openstudiolandscapes', docker_registry_access=<DockerRegistryAccess.public: 'public'>, docker_registry_protocol=<DockerRegistryProtocol.https: 'https'>, docker_registry_fqdn='registry.openstudiolandscapes.lan', docker_registry_port=5000, docker_registry_username='registry-user', docker_registry_password='registry-password'), docker_pull_policy=<DockerPullPolicy.always: 'always'>), openstudiolandscapes__rez_config=RezConfigModel(rez_version='3.3.0', REZ_LOCAL_PACKAGES_PATH=PosixPath('~/packages'), REZ_RELEASE_PACKAGES_PATH=PosixPath('~/.rez/packages/int'), REZ_EXTERNAL_PACKAGES_PATH=PosixPath('/data/share/rez-packages/packages'), apt_packages_rez=['binutils']), apt_packages_base=['git', 'ca-certificates', 'htop', 'file', 'tzdata', 'curl', 'wget', 'ffmpeg', 'libegl1', 'libsm6', 'libglu1-mesa', 'libxss1', 'sudo', 'xz-utils', 'xvfb', 'xauth'], apt_packages_build_python311=['build-essential', 'pkg-config', 'zlib1g-dev', 'libncurses5-dev', 'libgdbm-dev', 'libnss3-dev', 'libssl-dev', 'libreadline-dev', 'libffi-dev', 'libsqlite3-dev', 'libbz2-dev', 'iproute2', 'liblzma-dev'], pip_packages=[], openstudiolandscapes__domain_lan='openstudiolandscapes.lan', openstudiolandscapes__human_readable_ids=True, sudo_method=<SudoMethod.PKEXEC: 'pkexec'>, global_bind_volumes=['/data/share:/data/share:rw'], global_environment_variables={'OPENSTUDIOLANDSCAPES__DAGSTER_JOBS_IN': '/data/share/in'}, tz='Europe/UTC')

        config_feature.distribution = feature_dist
        LOGGER.debug(f"{config_feature.distribution = }")
        # config_feature.distribution = <importlib.metadata.PathDistribution object at 0x7fe647853dd0>

        feature.config = config_feature
        LOGGER.debug(f"{feature.config = }")
        # feature.config = Feature(
        #     [
        #         'env={}',
        #         'local_bind_volumes=[]',
        #         'local_environment_variables={}',
        #         "config_engine=openstudiolandscapes__docker_config=DockerConfigModel(
        #             use_registry=True,
        #             no_cache=False,
        #             docker_registry_config=DockerRegistryConfig(
        #                 docker_push=True,
        #                 docker_pull=True,
        #                 docker_repository_name='openstudiolandscapes',
        #                 docker_registry_access=<DockerRegistryAccess.public: 'public'>,
        #                 docker_registry_protocol=<DockerRegistryProtocol.https: 'https'>,
        #                 docker_registry_fqdn='registry.openstudiolandscapes.lan',
        #                 docker_registry_port=5000,
        #                 docker_registry_username='registry-user',
        #                 docker_registry_password='registry-password'
        #             ),
        #             docker_pull_policy=<DockerPullPolicy.always: 'always'>
        #         )
        #         openstudiolandscapes__rez_config=RezConfigModel(
        #             rez_version='3.3.0',
        #             REZ_LOCAL_PACKAGES_PATH=PosixPath('~/packages'),
        #             REZ_RELEASE_PACKAGES_PATH=PosixPath('~/.rez/packages/int'),
        #             REZ_EXTERNAL_PACKAGES_PATH=PosixPath('/data/share/rez-packages/packages'),
        #             apt_packages_rez=['binutils']
        #         )
        #         apt_packages_base=['git', 'ca-certificates', 'htop', 'file', 'tzdata', 'curl', 'wget', 'ffmpeg', 'libegl1', 'libsm6', 'libglu1-mesa', 'libxss1', 'sudo', 'xz-utils', 'xvfb', 'xauth']
        #         apt_packages_build_python311=['build-essential', 'pkg-config', 'zlib1g-dev', 'libncurses5-dev', 'libgdbm-dev', 'libnss3-dev', 'libssl-dev', 'libreadline-dev', 'libffi-dev', 'libsqlite3-dev', 'libbz2-dev', 'iproute2', 'liblzma-dev']
        #         pip_packages=[]
        #         openstudiolandscapes__domain_lan='openstudiolandscapes.lan'
        #         openstudiolandscapes__human_readable_ids=True
        #         sudo_method=<SudoMethod.PKEXEC: 'pkexec'>
        #         global_bind_volumes=['/data/share:/data/share:rw']
        #         global_environment_variables={'OPENSTUDIOLANDSCAPES__DAGSTER_JOBS_IN': '/data/share/in'}
        #         tz='Europe/UTC'",
        #
        #         'distribution=<importlib.metadata.PathDistribution object at 0x7fe9b533ecd0>',
        #         'group_name=OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20',
        #         "key_prefixes=['OpenStudioLandscapes_SESI_gcc_9_3_Houdini_20']",
        #         'enabled=True',
        #         'compose_scope=license_server',
        #         'feature_name=OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20',
        #         'docker_compose={DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml',
        #         'LICENSES_ACTIVE={DOT_FEATURES}/{FEATURE}/.payload/data/licenses',
        #         'HKEY_BIN={DOT_FEATURES}/{FEATURE}/.payload/bin/hkey-bin',
        #         'HSERVER={DOT_FEATURES}/{FEATURE}/.payload/bin/hserver',
        #         'LICENSES={DOT_FEATURES}/{FEATURE}/.payload/bin/licenses',
        #         'LICENSES_DISABLED={DOT_FEATURES}/{FEATURE}/.payload/bin/licenses.disabled',
        #         'SESICTRL={DOT_FEATURES}/{FEATURE}/.payload/bin/sesictrl',
        #         'SESINETD={DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd',
        #         'SESINETD_PEAK_USAGE_BIN={DOT_FEATURES}/{FEATURE}/.payload/bin/sesinetd_peak_usage.bin',
        #         'SESIUSAGE={DOT_FEATURES}/{FEATURE}/.payload/bin/sesiusage',
        #         'SESI_PORT_HOST=1717',
        #         'SESI_PORT_CONTAINER=1715',
        #         "apt_packages=['lsb-release']"
        #     ]
        # )

        dump_yaml(
            model_config=config_feature,
            file_path=config_yml_feature_expanded,
        )

    LOGGER.debug(f"{FeatureBaseModel.subclasses = }")
    # FeatureBaseModel.subclasses = {
    #     [...]
    #     'OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20': <class 'OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models.Config'>,
    #     [...]
    # }

    commit_configs(
        config_store_repo=config_store_repo,
        fresh_repo=fresh_repo,
    )

    LOGGER.info(f"Bootstrapping finished successfully.")

    return None


if __name__ == "__main__":
    pass

else:
    DISCOVERED_MODELS: Dict[str, OpenStudioLandscapesDiscoveredFeature] = {}

    config_engine: ConfigEngine = get_config_engine()

    init(
        config_engine=config_engine,
        discovered_models=DISCOVERED_MODELS,
    )

    # Todo
    #  - [ ] improve type hint
    DYNAMIC_INS: Dict = get_dynamic_ins(
        imported_features=DISCOVERED_MODELS,
    )
