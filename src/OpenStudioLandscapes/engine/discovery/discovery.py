"""
This is the Feature discovery engine for OpenStudioLandscapes.
"""

import importlib
import pathlib
from typing import List

import yaml
from dagster import get_dagster_logger
from pydantic import BaseModel, Field
from setuptools import find_namespace_packages

from OpenStudioLandscapes.engine.features import FeatureBase

LOGGER = get_dagster_logger(__name__)

# Important
# The Feature Git repositories have to physically exist locally.
# It's not enough to just pip install them from the repo directly, like:
# `pip install OpenStudioLandscapes-Ayon@git+https://github.com/michimussato/OpenStudioLandscapes-Ayon`
# Maybe one day...


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
    definitions: str = Field()
    models: str = Field()


DISCOVERED_MODELS = {}
for package in get_namespace_packages():
    module = OpenStudioLandscapesDiscoveredFeature(
        **{
            "definitions": get_definitions_path(package),
            "models": get_models_path(package),
        }
    )
    DISCOVERED_MODELS[package] = module

LOGGER.info(f"{DISCOVERED_MODELS = }")

LOGGER.info(f"{FeatureBase.subclasses = }")

SUCCESSFUL_MODULE_IMPORTS = []  # used in definitions.py (list of <module> objects)
IMPORTED_FEATURES = []  # used in dynamic asset imports

USABLE_FEATURES = []

for package, discovered_model in DISCOVERED_MODELS.items():

    LOGGER.info(f"{package = }")
    LOGGER.info(f"{discovered_model = }")
    try:
        _models = discovered_model.models
        _definitions = discovered_model.definitions
        LOGGER.info(f"{_models = }")
        models_object = importlib.import_module(_models)
        definitions_object = importlib.import_module(_definitions)
        LOGGER.info("Feature models import successful: '%s'" % models_object)
        LOGGER.info("Feature definitions import successful: '%s'" % definitions_object)
        USABLE_FEATURES.append(
            {
                "package": package,
                "discovered_model": discovered_model,
                "models": models_object,
                "definitions": definitions_object,
            }
        )
    except (ModuleNotFoundError, AttributeError) as e:
        LOGGER.error(
            "Feature import failed: '%s'" % discovered_model.models
        )


# def get_engine_config() -> ConfigEngine:

# hardcoded for now
CONFIG_STORE = pathlib.Path.home() / ".config" / "OpenStudioLandscapes" / "config-store"

for feature in USABLE_FEATURES:
    LOGGER.error(f"{feature = }")
    # feature = {'package': 'OpenStudioLandscapes-VERT.src.OpenStudioLandscapes.VERT', 'discovered_model': OpenStudioLandscapesDiscoveredFeature(definitions='OpenStudioLandscapes.VERT.definitions', models='OpenStudioLandscapes.VERT.config.models'), 'models': <module 'OpenStudioLandscapes.VERT.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-VERT/src/OpenStudioLandscapes/VERT/config/models.py'>, 'definitions': <module 'OpenStudioLandscapes.VERT.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-VERT/src/OpenStudioLandscapes/VERT/definitions.py'>, 'Config': Config(enabled=True, registry=<DockerRegistryProtocol.http: 'http'>, compose_scope='default', feature_name='OpenStudioLandscapes-VERT', group_name='VERT', key_prefixes=['VERT'], docker_compose='{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml', definitions='OpenStudioLandscapes.VERT.definitions', docker_compose_override='{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.override.yml', vert_port_container=80, vert_port_host=3344, repository_url='https://github.com/VERT-sh/VERT.git', repository_branch='main', repository_subdir='VERT', docker_compose_yml='docker-compose.yml', docker_compose_worker_yml='docker-compose.worker.yml')}
    # load config_blueprint.yml
    try:
        config_yml = CONFIG_STORE / feature["package"].split(".")[0] / "config.yml"
        with open(config_yml, "r") as f:
            LOGGER.info(f"Loading `config_blueprint.yml`: {config_yml = }")
            config_dict = yaml.safe_load(f)
            LOGGER.info(f"Loaded `config_blueprint.yml`: {config_yml = }")
    except FileNotFoundError:
        blue_print_yml = pathlib.Path(feature["models"].__file__).parent / "config_blueprint.yml"
        with open(blue_print_yml, "r") as f:
            LOGGER.info(f"Loading `config_blueprint.yml`: {blue_print_yml = }")
            config_dict = yaml.safe_load(f)
            LOGGER.info(f"Loaded `config_blueprint.yml`: {config_dict = }")

    config_model: FeatureBase = feature["models"].Config(**config_dict)
    LOGGER.info(f"{config_model = }")
    feature["Config"] = config_model


LOGGER.info(f"{FeatureBase.subclasses = }")

LOGGER.info(f"{USABLE_FEATURES = }")
