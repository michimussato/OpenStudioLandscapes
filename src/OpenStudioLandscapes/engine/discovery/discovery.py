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

from OpenStudioLandscapes.engine.config.models import FeatureBaseModel
from OpenStudioLandscapes.engine.features import FeatureDiscovery

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

# LOGGER.info(f"{json.loads(json.dumps(DISCOVERED_MODELS, indent=4, default=str)) = }")
# {
#     'OpenStudioLandscapes-NukeRLM-8.src.OpenStudioLandscapes.NukeRLM_8': "definitions='OpenStudioLandscapes.NukeRLM_8.definitions' models='OpenStudioLandscapes.NukeRLM_8.config.models'",
#     'OpenStudioLandscapes-Flamenco.src.OpenStudioLandscapes.Flamenco': "definitions='OpenStudioLandscapes.Flamenco.definitions' models='OpenStudioLandscapes.Flamenco.config.models'",
#     'OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20.src.OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20': "definitions='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.definitions' models='OpenStudioLandscapes.SESI_gcc_9_3_Houdini_20.config.models'",
#     'OpenStudioLandscapes-Deadline-10-2.src.OpenStudioLandscapes.Deadline_10_2': "definitions='OpenStudioLandscapes.Deadline_10_2.definitions' models='OpenStudioLandscapes.Deadline_10_2.config.models'",
#     'OpenStudioLandscapes-Syncthing.src.OpenStudioLandscapes.Syncthing': "definitions='OpenStudioLandscapes.Syncthing.definitions' models='OpenStudioLandscapes.Syncthing.config.models'",
#     'OpenStudioLandscapes-filebrowser.src.OpenStudioLandscapes.filebrowser': "definitions='OpenStudioLandscapes.filebrowser.definitions' models='OpenStudioLandscapes.filebrowser.config.models'",
#     'OpenStudioLandscapes-Dagster.src.OpenStudioLandscapes.Dagster': "definitions='OpenStudioLandscapes.Dagster.definitions' models='OpenStudioLandscapes.Dagster.config.models'",
#     'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu': "definitions='OpenStudioLandscapes.Kitsu.definitions' models='OpenStudioLandscapes.Kitsu.config.models'",
#     'OpenStudioLandscapes-Kitsu.src.OpenStudioLandscapes.Kitsu.config': "definitions='Kitsu.config.definitions' models='Kitsu.config.config.models'",
#     'OpenStudioLandscapes-OpenCue.src.OpenStudioLandscapes.OpenCue': "definitions='OpenStudioLandscapes.OpenCue.definitions' models='OpenStudioLandscapes.OpenCue.config.models'",
#     'OpenStudioLandscapes-Grafana.src.OpenStudioLandscapes.Grafana': "definitions='OpenStudioLandscapes.Grafana.definitions' models='OpenStudioLandscapes.Grafana.config.models'",
#     'OpenStudioLandscapes-LikeC4.src.OpenStudioLandscapes.LikeC4': "definitions='OpenStudioLandscapes.LikeC4.definitions' models='OpenStudioLandscapes.LikeC4.config.models'",
#     'OpenStudioLandscapes-Flamenco-Worker.src.OpenStudioLandscapes.Flamenco_Worker': "definitions='OpenStudioLandscapes.Flamenco_Worker.definitions' models='OpenStudioLandscapes.Flamenco_Worker.config.models'",
#     'OpenStudioLandscapes-RustDeskServer.src.OpenStudioLandscapes.RustDeskServer': "definitions='OpenStudioLandscapes.RustDeskServer.definitions' models='OpenStudioLandscapes.RustDeskServer.config.models'",
#     'OpenStudioLandscapes-Ayon.src.OpenStudioLandscapes.Ayon': "definitions='OpenStudioLandscapes.Ayon.definitions' models='OpenStudioLandscapes.Ayon.config.models'",
#     'OpenStudioLandscapes-Template.src.OpenStudioLandscapes.Template': "definitions='OpenStudioLandscapes.Template.definitions' models='OpenStudioLandscapes.Template.config.models'",
#     'OpenStudioLandscapes-Watchtower.src.OpenStudioLandscapes.Watchtower': "definitions='OpenStudioLandscapes.Watchtower.definitions' models='OpenStudioLandscapes.Watchtower.config.models'",
#     'OpenStudioLandscapes-Watchtower.src.OpenStudioLandscapes.Watchtower.config': "definitions='Watchtower.config.definitions' models='Watchtower.config.config.models'",
#     'OpenStudioLandscapes-Deadline-10-2-Worker.src.OpenStudioLandscapes.Deadline_10_2_Worker': "definitions='OpenStudioLandscapes.Deadline_10_2_Worker.definitions' models='OpenStudioLandscapes.Deadline_10_2_Worker.config.models'",
#     'OpenStudioLandscapes-Twingate.src.OpenStudioLandscapes.Twingate': "definitions='OpenStudioLandscapes.Twingate.definitions' models='OpenStudioLandscapes.Twingate.config.models'",
#     'OpenStudioLandscapes-VERT.src.OpenStudioLandscapes.VERT': "definitions='OpenStudioLandscapes.VERT.definitions' models='OpenStudioLandscapes.VERT.config.models'",
#     'OpenStudioLandscapes-VERT.src.OpenStudioLandscapes.VERT.config': "definitions='VERT.config.definitions' models='VERT.config.config.models'",
# }

LOGGER.info(f"{FeatureDiscovery.subclasses = }")

SUCCESSFUL_MODULE_IMPORTS = []  # used in definitions.py (list of <module> objects)
IMPORTED_FEATURES = []  # used in dynamic asset imports

FUNCTIONAL_FEATURES = []

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
        FUNCTIONAL_FEATURES.append(
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

for feature in FUNCTIONAL_FEATURES:
    LOGGER.error(f"{feature = }")
    # feature = {'package': 'OpenStudioLandscapes-VERT.src.OpenStudioLandscapes.VERT', 'discovered_model': OpenStudioLandscapesDiscoveredFeature(definitions='OpenStudioLandscapes.VERT.definitions', models='OpenStudioLandscapes.VERT.config.models'), 'models': <module 'OpenStudioLandscapes.VERT.config.models' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-VERT/src/OpenStudioLandscapes/VERT/config/models.py'>, 'definitions': <module 'OpenStudioLandscapes.VERT.definitions' from '/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-VERT/src/OpenStudioLandscapes/VERT/definitions.py'>, 'Config': Config(enabled=True, registry=<DockerRegistryProtocol.http: 'http'>, compose_scope='default', feature_name='OpenStudioLandscapes-VERT', group_name='VERT', key_prefixes=['VERT'], docker_compose='{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml', definitions='OpenStudioLandscapes.VERT.definitions', docker_compose_override='{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.override.yml', vert_port_container=80, vert_port_host=3344, repository_url='https://github.com/VERT-sh/VERT.git', repository_branch='main', repository_subdir='VERT', docker_compose_yml='docker-compose.yml', docker_compose_worker_yml='docker-compose.worker.yml')}
    # load config_blueprint.yml
    config_yml = CONFIG_STORE / feature["package"].split(".")[0] / "config.yml"

    if config_yml.exists():
        with open(config_yml, "r") as f:
            LOGGER.info(f"Loading `config_blueprint.yml`: {config_yml = }")
            config_dict = yaml.safe_load(f)
            LOGGER.info(f"Loaded `config_blueprint.yml`: {config_yml = }")
    else:
        LOGGER.warning("Loading config from `CONFIG_STR`...")
        try:
            CONFIG_STR = feature["models"].CONFIG_STR
            LOGGER.debug(f"`CONFIG_STR` for {feature['package']} successfully read.")
        except (KeyError, AttributeError) as e:
            LOGGER.error(f"`CONFIG_STR` for {feature['package']} not found. Ignoring.")
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
    config_model: FeatureBaseModel = feature["models"].Config(**config_dict)
    # LOGGER.error(f"{type(config_model) = }")
    # if isinstance(config_model, FeatureBaseModel):
    #     raise TypeError()
    LOGGER.info(f"{config_model = }")
    feature["Config"] = config_model

LOGGER.info(f"{FeatureDiscovery.subclasses = }")

LOGGER.info(f"{FUNCTIONAL_FEATURES = }")

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
