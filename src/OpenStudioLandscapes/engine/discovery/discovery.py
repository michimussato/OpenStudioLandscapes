"""
This is the Feature discovery engine for OpenStudioLandscapes.
"""

import importlib
import os
import pathlib
from importlib import metadata
from importlib.metadata import Distribution
from types import ModuleType
from typing import Dict, List, Tuple

import git
import yaml
from dagster import get_dagster_logger
from pydantic import BaseModel, ConfigDict, Field
from setuptools import find_namespace_packages

from OpenStudioLandscapes.engine import dist as dist_engine
from OpenStudioLandscapes.engine.config.models import CONFIG_STR as ENGINE_CONFIG_STR
from OpenStudioLandscapes.engine.config.models import ConfigEngine, FeatureBaseModel

LOGGER = get_dagster_logger(__name__)


LOGGER.info("Start bootstrapping...")


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
        default="~/.config/OpenStudioLandscapes/config-store",
    )
)


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
        parents=True, exist_ok=True
    )
    LOGGER.info(
        f"Repo dir created: {OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.expanduser().as_posix()}."
    )

config_store_repo, fresh_repo = init_config_store(
    OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT
)


def get_config_engine() -> ConfigEngine:
    """
    Get the Engine Configuration.

    Returns:
        ConfigEngine
    """

    def get_config_dict() -> Dict:
        # Specify the `config.yml` for the engine.
        # Hard coding this is a good and predictable way
        # to implement this.
        LOGGER.info(f"{dist_engine.name = }")
        engine_config_yml: pathlib.Path = (
            OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.joinpath(
                dist_engine.name,
                "config.yml",
            )
        )
        engine_config_yml_expanded: pathlib.Path = engine_config_yml.expanduser()
        LOGGER.info(f"{engine_config_yml = }")
        LOGGER.info(f"{engine_config_yml_expanded = }")

        # Create the `config.yml` for the engine
        # with the default `CONFIG_STR` if
        # it does not exist
        if not engine_config_yml_expanded.exists():
            engine_config_yml_expanded.parent.mkdir(parents=True, exist_ok=True)
            engine_config_yml_expanded.write_text(ENGINE_CONFIG_STR)

        # Read the `config.yml` as a str
        engine_config_str: str = engine_config_yml_expanded.read_text()

        engine_config_dict: Dict = yaml.safe_load(engine_config_str)

        return engine_config_dict

    engine_config_dict = get_config_dict()

    config_engine: ConfigEngine = ConfigEngine(**engine_config_dict)
    LOGGER.info(f"{config_engine = }")

    return config_engine


config_engine = get_config_engine()


def get_namespace_packages(where=pathlib.Path.cwd() / ".features") -> List[str]:
    LOGGER.info(
        "Getting installed OpenStudioLandscapes namespace packages from '%s'...", where
    )
    namespace_packages = find_namespace_packages(
        where=where,
        include=["*src.OpenStudioLandscapes.*"],
    )
    LOGGER.info(f"{namespace_packages = }")
    # ['OpenStudioLandscapes-NukeRLM-8.src.OpenStudioLandscapes.NukeRLM_8', ...]
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


class OpenStudioLandscapesDiscoveredFeature(BaseModel):
    # ModuleType Fields:
    # pydantic.errors.PydanticSchemaGenerationError:
    #   Unable to generate pydantic-core schema for <class 'module'>.
    #   Set `arbitrary_types_allowed=True` in the model_config to
    #   ignore this error or implement `__get_pydantic_core_schema__`
    #   on your type to fully support it.
    model_config = ConfigDict(
        # This disables model checks for all fields.
        # More info here:
        # - https://stackoverflow.com/a/78379656/2207196
        arbitrary_types_allowed=True,
    )

    definitions: str = Field()
    definitions_object: ModuleType = Field(
        default=None,
    )

    models: str = Field()
    models_object: ModuleType = Field(
        default=None,
    )

    config: FeatureBaseModel = Field(
        default=None,
        # default_factory=FeatureBaseModel,
    )


def try_import_discovered(
    package: str,
    discovered_model: OpenStudioLandscapesDiscoveredFeature,
) -> Tuple[ModuleType, ModuleType]:
    """Try to import a discovered model from a package."""

    LOGGER.info(f"{package = }")
    LOGGER.info(f"{discovered_model = }")
    try:
        _models = discovered_model.models
        _definitions = discovered_model.definitions
        LOGGER.info(f"{_models = }")
        LOGGER.info(f"{_definitions = }")
        models_object: ModuleType = importlib.import_module(_models)
        definitions_object: ModuleType = importlib.import_module(_definitions)
        LOGGER.info("Feature models import successful: '%s'" % models_object)
        LOGGER.info("Feature definitions import successful: '%s'" % definitions_object)
        return models_object, definitions_object
    except (ModuleNotFoundError, AttributeError) as e:
        raise ImportError(e) from e


DISCOVERED_MODELS = {}


for package in get_namespace_packages():
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
        models_object, definitions_object = try_import_discovered(package, module)
    except ImportError as e:
        LOGGER.error("Feature import failed: '%s'" % package)
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

    DISCOVERED_MODELS[package] = module


LOGGER.info(f"{DISCOVERED_MODELS = }")


def get_config_dict_feature(
    package: str,
    feature: OpenStudioLandscapesDiscoveredFeature,
) -> Dict:
    distribution: Distribution = metadata.distribution(package.partition(".")[0])

    # Create the `config.yml` for the feature
    # with the default `CONFIG_STR` if
    # it does not exist
    config_yml_feature: pathlib.Path = OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.joinpath(
        distribution.name,
        "config.yml",
    )
    LOGGER.info(f"{config_yml_feature = }")
    config_yml_feature_expanded = config_yml_feature.expanduser()

    if not config_yml_feature_expanded.exists():
        config_yml_feature_expanded.parent.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Loading config from `CONFIG_STR`...")
        try:
            CONFIG_STR = feature.models_object.CONFIG_STR
            LOGGER.info(f"`CONFIG_STR` for {package} successfully read.")
        except (KeyError, AttributeError) as e:
            raise ImportError(e) from e

        config_yml_feature_expanded.write_text(CONFIG_STR)

    # Read the `config.yml` as a str
    config_str_feature: str = config_yml_feature_expanded.read_text()
    LOGGER.info(f"{config_str_feature = }")

    config_dict_feature: Dict = yaml.safe_load(config_str_feature)

    # Also inject the ConfigEngine object
    config_dict_feature["config_engine"] = config_engine
    # and the Distribution object
    config_dict_feature["distribution"] = distribution
    LOGGER.info(f"{config_dict_feature = }")

    return config_dict_feature


# Annotate the types before the loop
# References:
# - https://stackoverflow.com/a/41641489/2207196
package: str
feature: OpenStudioLandscapesDiscoveredFeature
for package, feature in DISCOVERED_MODELS.items():
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

    try:
        config_dict_feature = get_config_dict_feature(package, feature)
    except ImportError as e:
        LOGGER.error(f"`CONFIG_STR` for {package} not found. Ignoring.")
        continue

    # Config is the `OpenStudioLandscapes.<FEATURE>.config.models.Config` object.
    #
    # The `OpenStudioLandscapes.<FEATURE>.config.models.Config` itself inherits
    # from `OpenStudioLandscapes.engine.config.models.FeatureBaseModel`.
    config_model_object: FeatureBaseModel = feature.models_object.Config(
        **config_dict_feature
    )
    LOGGER.info(f"{config_model_object = }")
    feature.config = config_model_object


LOGGER.info(f"{FeatureBaseModel.subclasses = }")
#  FeatureBaseModel.subclasses =
#  {
#      'OpenStudioLandscapes-Kitsu': <class 'OpenStudioLandscapes.Kitsu.config.models.Config'>,
#      'OpenStudioLandscapes-Watchtower': <class 'OpenStudioLandscapes.Watchtower.config.models.Config'>,
#      'OpenStudioLandscapes-VERT': <class 'OpenStudioLandscapes.VERT.config.models.Config'>,
#  }


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


LOGGER.info(f"Bootstrapping finished successfully.")
