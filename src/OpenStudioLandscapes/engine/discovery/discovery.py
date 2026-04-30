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
  - This mechanisma, however, allows to dynamically
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
  - update_config_yml
  - Repo initialization
    - init_config_store()


The logic current does:
- not add documenting comments to the initial YAML files
- add new keys from model fields to the YAML
- not remove keys from the YAML of non-existing model fields
- keep comments in the YAML files
  - [How to Update YAML in Python While Preserving Order and Comments: A Step-by-Step Guide](https://www.w3reference.com/blog/python-yaml-update-preserving-order-and-comments/)
"""
import importlib
from collections import OrderedDict
import json
import os
import pathlib
from importlib import metadata
from importlib.metadata import Distribution
from types import ModuleType
from typing import Dict, List, Tuple, Union

import git
import ruamel.yaml
from dagster import get_dagster_logger
from setuptools import find_namespace_packages

from OpenStudioLandscapes.engine import dist as dist_engine
from OpenStudioLandscapes.engine.config.models import (
    ConfigEngine,
    FeatureBaseModel,
    OpenStudioLandscapesDiscoveredFeature,
)

class OpenStudioLandscapesDiscoveryException(Exception):
    pass

LOGGER = get_dagster_logger(__name__)


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

    if data is None:
        raise OpenStudioLandscapesDiscoveryException(
            "Could not load YAML file: \n"
            f"{file_path = }\n"
            f"{data = }\n"
        )

        # Seems to be a bit random...
        # - file currently open?

        # In process 392288: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20/config.yml')
        # data = None

        # In process 400434: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-NukeRLM-8/config.yml')
        # data = None

        # In process 399991: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-OpenCue/config.yml')
        # data = None

        # In process 399481: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-Deadline-10-2/config.yml')
        # data = None

        # In process 511464: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes/config.yml')
        # data = None

        # In process 511343: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-Flamenco/config.yml')
        # data = None

        # In process 556689: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-Kitsu/config.yml')
        # data = None

        # In process 556617: OpenStudioLandscapes.engine.discovery.discovery.OpenStudioLandscapesDiscoveryException: Could not load YAML file:
        # file_path = PosixPath('/home/michael/.config/OpenStudioLandscapes/config-store/OpenStudioLandscapes-Dagster/config.yml')
        # data = None

    return data


def dump_yaml(
    model_config: Union[ConfigEngine, FeatureBaseModel],
    file_path: pathlib.Path,
):
    """Save YAML data to a file, preserving comments/order."""

    # if file_path.exists() is not necessary - part of get_config()
    current_config_: ruamel.yaml.CommentedMap = get_config(
        file_path_config_yaml=file_path,
    )

    file_path.parent.mkdir(parents=True, exist_ok=True)

    model_dump_json: str = model_config.model_dump_json(indent=2, fallback=str)
    model_dump_dict: Dict = json.loads(model_dump_json)

    # update current_config_
    current_config_.update(model_dump_dict)

    if file_path.exists():
        # Develop some logic so that
        # the existing file does not just get
        # overwritten just like that.
        # Keeping control over file handle
        # concurrency with Dagster is not straight
        # forward it seems.
        # Of course, we need to make sure that
        # new/changed model fields don't result
        # in non-functional situations.
        # - "Migration" logic?
        pass
    else:
        yaml_ = ruamel.yaml.YAML(typ="rt")
        yaml_.indent(
            mapping=2,
            sequence=2,
            offset=0,
        )  # Match original indentation
        with open(file_path, "w") as f:
            yaml_.dump(current_config_, f)


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
        data: ruamel.yaml.CommentedMap = load_yaml(
            file_path=file_path_config_yaml,
        )
    else:
        # CommentedMap needs an OrderedDict.
        # Standard dict does not work.
        data: ruamel.yaml.CommentedMap = ruamel.yaml.CommentedMap(
            OrderedDict()
        )

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

    LOGGER.info(f"{dist.name = }")
    config_yml: pathlib.Path = (
        OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.joinpath(
            dist.name,
            "config.yml",
        )
    )
    config_yml_expanded: pathlib.Path = config_yml.expanduser()
    LOGGER.info(f"{config_yml = }")
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


REPO_INITIALIZED = False


def init_config_store(
    root: pathlib.Path,
) -> Tuple[git.Repo, bool]:
    # Get Git repo
    try:
        fresh_repo = False
        r = git.Repo(root.expanduser())
        LOGGER.info(f"Using existing repo: {r.common_dir}.")
    except git.exc.InvalidGitRepositoryError:
        fresh_repo = True
        # Create Repo if dir is not a Git repo
        # https://gitpython.readthedocs.io/en/stable/tutorial.html#initializing-a-repository
        r = git.Repo.init(root.expanduser())
        LOGGER.info(f"New repo created: {r.common_dir}.")

    global REPO_INITIALIZED
    REPO_INITIALIZED = True

    return r, fresh_repo


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
    LOGGER.info(f"{config_engine = }")

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
    LOGGER.info(f"{namespace_packages_ = }")
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
    LOGGER.info(f"{discovered_model = }")
    try:
        _models = discovered_model.models
        LOGGER.info(f"{_models = }")
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
        LOGGER.info(f"{_definitions = }")
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
    discovered_models: Dict,
) -> Dict[str, ModuleType]:

    for package in get_namespace_packages(
        where=pathlib.Path.cwd().joinpath(".features"),
    ):
        feature_dict = {
            "definitions": get_definitions_path(package),
            "models": get_models_path(package),
        }
        module = OpenStudioLandscapesDiscoveredFeature(**feature_dict)
        # 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu':
        #     OpenStudioLandscapesDiscoveredFeature(
        #         definitions='OpenStudioLandscapes.Kitsu.definitions',
        #         models='OpenStudioLandscapes.Kitsu.config.models',
        #         config=None,
        #     ),

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
        module.models_object = models_object
        # 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu':
        #     OpenStudioLandscapesDiscoveredFeature(
        #         definitions='OpenStudioLandscapes.Kitsu.definitions',
        #         definitions_object=<module 'OpenStudioLandscapes.Kitsu.definitions'
        #             from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/definitions.py'>,
        #         models='OpenStudioLandscapes.Kitsu.config.models',
        #         models_object=<module 'OpenStudioLandscapes.Kitsu.config.models'
        #             from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/config/models.py'>,
        #         config=None
        #     ),

        discovered_models[package] = module

    LOGGER.info(f"{discovered_models = }")

    # Annotate the types before the loop
    # References:
    # - https://stackoverflow.com/a/41641489/2207196
    package: str
    feature: OpenStudioLandscapesDiscoveredFeature
    for package, feature in discovered_models.items():
        LOGGER.info(f"{package = }")
        # package =
        # 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu'
        LOGGER.info(f"{feature = }")
        # feature =
        # OpenStudioLandscapesDiscoveredFeature(
        #     definitions='OpenStudioLandscapes.Kitsu.definitions',
        #     definitions_object=<module 'OpenStudioLandscapes.Kitsu.definitions'
        #         from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/definitions.py'>,
        #     models='OpenStudioLandscapes.Kitsu.config.models',
        #     models_object=<module 'OpenStudioLandscapes.Kitsu.config.models'
        #         from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/config/models.py'>,
        #     config=None
        # )

        feature_dist: Distribution = metadata.distribution(package)

        config_yml_feature_expanded: pathlib.Path = get_absolute_config_path(
            dist=feature_dist,
        )

        feature_config_dict: ruamel.yaml.CommentedMap = get_config(
            file_path_config_yaml=config_yml_feature_expanded,
        )

        # Also inject the ConfigEngine object
        LOGGER.debug(f"{feature_config_dict = }")
        LOGGER.debug(f"{config_engine = }")
        LOGGER.debug(f"{feature_dist = }")
        LOGGER.info(f"{feature_config_dict = }")

        config_feature: FeatureBaseModel = feature.models_object.Config(
            **feature_config_dict,
        )
        # Also inject the ConfigEngine object
        config_feature.config_engine = config_engine
        config_feature.distribution = feature_dist
        LOGGER.info(f"{config_feature = }")
        feature.config = config_feature

        dump_yaml(
            model_config=config_feature,
            file_path=config_yml_feature_expanded,
        )

    LOGGER.info(f"{FeatureBaseModel.subclasses = }")
    #  FeatureBaseModel.subclasses =
    #  {
    #      'OpenStudioLandscapes-Kitsu': <class 'OpenStudioLandscapes.Kitsu.config.models.Config'>,
    #      'OpenStudioLandscapes-Watchtower': <class 'OpenStudioLandscapes.Watchtower.config.models.Config'>,
    #      'OpenStudioLandscapes-VERT': <class 'OpenStudioLandscapes.VERT.config.models.Config'>,
    #  }

    def commit_configs() -> None:

        if REPO_INITIALIZED:
            # Add all files to tracked files in Git repo
            if fresh_repo:
                LOGGER.info(f"Add files to tracked file...")
                config_store_repo.index.add("*")
                LOGGER.info(f"Making initial commit...")
                config_store_repo.index.commit("Initial Commit")
                LOGGER.info(f"Initial Commit successful.")
            else:
                if config_store_repo.is_dirty():
                    # config_store_repo.git.status("--porcelain")
                    LOGGER.warning(
                        f"Config Store '{config_store_repo.common_dir}' has uncommited changes: "
                        f"{config_store_repo.git.status()}"
                    )
                    LOGGER.info("Manual commit necessary.")

    commit_configs()

    LOGGER.info(f"Bootstrapping finished successfully.")

    return discovered_models


if __name__ == "__main__":
    pass

else:
    DISCOVERED_MODELS: Dict[str, ModuleType] = {}

    config_engine: ConfigEngine = get_config_engine()

    init(
        config_engine=config_engine,
        discovered_models=DISCOVERED_MODELS,
    )
