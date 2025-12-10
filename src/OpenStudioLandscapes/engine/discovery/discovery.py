"""
This is the Feature discovery engine for OpenStudioLandscapes.
"""

import importlib
import os
from types import ModuleType
import pathlib
from typing import List, Tuple, Dict

import yaml
from dagster import get_dagster_logger
from pydantic import BaseModel, Field, ConfigDict
from setuptools import find_namespace_packages

from OpenStudioLandscapes.engine.config.models import FeatureBaseModel, ConfigEngine
from OpenStudioLandscapes.engine.config.models import CONFIG_STR as ENGINE_CONFIG_STR
from OpenStudioLandscapes.engine.features import FeatureDiscovery

LOGGER = get_dagster_logger(__name__)


# Important
# The Feature Git repositories have to physically exist locally.
# It's not enough to just pip install them from the repo directly, like:
# `pip install OpenStudioLandscapes-Ayon@git+https://github.com/michimussato/OpenStudioLandscapes-Ayon`
# Maybe one day...


# Get the openstudiolandscapes__configstore_root
OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get(
        "OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
        default="~/.config/OpenStudioLandscapes/config-store",
    )
)


def get_config_engine() -> ConfigEngine:
    """
    Get the Engine Configuration.

    Returns:
        ConfigEngine
    """

    # Specify the `config.yml` for the engine.
    # Hard coding this is a good and predictable way
    # to implement this.
    engine_config_yml: pathlib.Path = (
        OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.expanduser().joinpath(
            "OpenStudioLandscapes-Engine",
            "config.yml",
        )
    )
    LOGGER.error(f"{engine_config_yml = }")

    # Create the `config.yml` for the engine
    # with the default `CONFIG_STR` if
    # it does not exist
    if not engine_config_yml.exists():
        engine_config_yml.parent.mkdir(parents=True, exist_ok=True)
        engine_config_yml.write_text(ENGINE_CONFIG_STR)

    # Read the `config.yml` as a str
    engine_config_str: str = engine_config_yml.read_text()

    engine_config_dict: Dict = yaml.safe_load(engine_config_str)
    config_engine: ConfigEngine = ConfigEngine(**engine_config_dict)

    LOGGER.info(f"{config_engine = }")
    return config_engine


config_engine = get_config_engine()


def get_namespace_packages(where=pathlib.Path.cwd() / ".features") -> List[str]:
    LOGGER.info("Getting installed OpenStudioLandscapes namespace packages from '%s'...", where)
    namespace_packages = find_namespace_packages(
        where=where,
        include=["*src.OpenStudioLandscapes.*"],
    )
    LOGGER.info(f"{namespace_packages = }")
    # ['OpenStudioLandscapes-NukeRLM-8.src.OpenStudioLandscapes.NukeRLM_8', ...]
    return namespace_packages


def get_definitions_path(namespace_package) -> str:
    LOGGER.info("Converting namespace package path to definitions path: '%s'...", namespace_package)
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
    LOGGER.info("Converting namespace package path to models path: '%s'...", namespace_package)
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
    module = OpenStudioLandscapesDiscoveredFeature(
        **feature_dict
    )
    # 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu':
    #     OpenStudioLandscapesDiscoveredFeature(
    #         definitions='OpenStudioLandscapes.Kitsu.definitions',
    #         models='OpenStudioLandscapes.Kitsu.config.models',
    #         config=None,
    #     ),

    try:
        models_object, definitions_object = try_import_discovered(package, module)
    except ImportError as e:
        LOGGER.error(
            "Feature import failed: '%s'" % package
        )
        continue

    module.definitions_object = definitions_object
    module.models_object = models_object
    # 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu':
    #     OpenStudioLandscapesDiscoveredFeature(
    #         definitions='OpenStudioLandscapes.Kitsu.definitions',
    #         definitions_object=<module 'OpenStudioLandscapes.Kitsu.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/definitions.py'>,
    #         models='OpenStudioLandscapes.Kitsu.config.models',
    #         models_object=<module 'OpenStudioLandscapes.Kitsu.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/config/models.py'>,
    #         config=None
    #     ),

    DISCOVERED_MODELS[package] = module


LOGGER.info(f"{DISCOVERED_MODELS = }")

# LOGGER.info(f"{FeatureDiscovery.subclasses = }")

# SUCCESSFUL_MODULE_IMPORTS = []  # used in definitions.py (list of <module> objects)
# IMPORTED_FEATURES = []  # used in dynamic asset imports
#
# FUNCTIONAL_FEATURES = []


# CONFIG_STORE = config_engine.openstudiolandscapes__configstore_root


# Annotate the types before the loop
# References:
# - https://stackoverflow.com/a/41641489/2207196
package: str
feature: OpenStudioLandscapesDiscoveredFeature
for package, feature in DISCOVERED_MODELS.items():
    LOGGER.error(f"{package = }")
    # package =
    # 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu'
    LOGGER.error(f"{feature = }")
    # feature =
    # OpenStudioLandscapesDiscoveredFeature(
    #     definitions='OpenStudioLandscapes.Kitsu.definitions',
    #     definitions_object=<module 'OpenStudioLandscapes.Kitsu.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/definitions.py'>,
    #     models='OpenStudioLandscapes.Kitsu.config.models',
    #     models_object=<module 'OpenStudioLandscapes.Kitsu.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/config/models.py'>,
    #     config=None
    # )

    config_yml = OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT / package.split(".")[0] / "config.yml"

    if config_yml.exists():
        with open(config_yml, "r") as f:
            LOGGER.info(f"Loading `config_blueprint.yml`: {config_yml = }")
            config_dict = yaml.safe_load(f)
            LOGGER.info(f"Loaded `config_blueprint.yml`: {config_yml = }")
    else:
        LOGGER.warning("Loading config from `CONFIG_STR`...")
        try:
            CONFIG_STR = feature.models_object.CONFIG_STR
            LOGGER.debug(f"`CONFIG_STR` for {package} successfully read.")
        except (KeyError, AttributeError) as e:
            LOGGER.error(f"`CONFIG_STR` for {package} not found. Ignoring.")
            continue
        LOGGER.debug(f"{CONFIG_STR = }")
        config_dict = yaml.safe_load(CONFIG_STR)
        LOGGER.debug(f"{config_dict = }")
        # blue_print_yml = pathlib.Path(feature["models"].__file__).parent / "config_blueprint.yml"
        # with open(blue_print_yml, "r") as f:
        #     LOGGER.info(f"Loading `config_blueprint.yml`: {blue_print_yml = }")
        #     config_dict = yaml.safe_load(f)
        #     LOGGER.info(f"Loaded `config_blueprint.yml`: {config_dict = }")

    # Config is the `OpenStudioLandscapes.<FEATURE>.config.models.Config` object.
    #
    # The `OpenStudioLandscapes.<FEATURE>.config.models.Config` itself inherits
    # from `OpenStudioLandscapes.engine.config.models.FeatureBaseModel`.
    #
    # However, there is also the `OpenStudioLandscapes.engine.features.feature.FeatureDiscovery`
    # model.
    config_model: FeatureBaseModel = feature.models_object.Config(**config_dict)
    LOGGER.info(f"{config_model = }")
    feature.config = config_model

LOGGER.info(f"{FeatureDiscovery.subclasses = }")

# LOGGER.info(f"{json.loads(json.dumps(FUNCTIONAL_FEATURES, indent=4, default=str)) = }")
# json.loads(json.dumps(FUNCTIONAL_FEATURES, indent=4, default=str)) =
# [
#     {'package': 'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu',
#      'discovered_model': "definitions='OpenStudioLandscapes.Kitsu.definitions' models='OpenStudioLandscapes.Kitsu.config.models'",
#      'models': "<module 'OpenStudioLandscapes.Kitsu.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/config/models.py'>",
#      'definitions': "<module 'OpenStudioLandscapes.Kitsu.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/src/OpenStudioLandscapes/Kitsu/definitions.py'>",
#      'Config': 'OpenStudioLandscapes-Kitsu'},
#     {'package': 'OpenStudioLandscapes-Watchtower.src.OpenStudioLandscapes.Watchtower',
#      'discovered_model': "definitions='OpenStudioLandscapes.Watchtower.definitions' models='OpenStudioLandscapes.Watchtower.config.models'",
#      'models': "<module 'OpenStudioLandscapes.Watchtower.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Watchtower/src/OpenStudioLandscapes/Watchtower/config/models.py'>",
#      'definitions': "<module 'OpenStudioLandscapes.Watchtower.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Watchtower/src/OpenStudioLandscapes/Watchtower/definitions.py'>",
#      'Config': 'OpenStudioLandscapes-Watchtower'},
#     {'package': 'OpenStudioLandscapes-VERT.src.OpenStudioLandscapes.VERT',
#      'discovered_model': "definitions='OpenStudioLandscapes.VERT.definitions' models='OpenStudioLandscapes.VERT.config.models'",
#      'models': "<module 'OpenStudioLandscapes.VERT.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-VERT/src/OpenStudioLandscapes/VERT/config/models.py'>",
#      'definitions': "<module 'OpenStudioLandscapes.VERT.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-VERT/src/OpenStudioLandscapes/VERT/definitions.py'>",
#      'Config': 'OpenStudioLandscapes-VERT'}
# ]
