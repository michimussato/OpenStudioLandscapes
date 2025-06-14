__all__ = [
    "PREFIX_COMPOSE_SCOPE",
    "DOCKER_CONFIG",
    "DOCKER_USE_CACHE_BASE",
    "DOCKER_USE_CACHE_GLOBAL",
    "ASSET_HEADER_BASE_ENV",
    "ASSET_HEADER_BASE",
    "ASSET_HEADER_LANDSCAPE_MAP",
    "ASSET_HEADER_COMPOSE_LICENSE_SERVER",
    "ASSET_HEADER_COMPOSE",
    "ASSET_HEADER_COMPOSE_WORKER",
    "ASSET_HEADER_COMPOSE_LICENSE_SERVER",
    "DOCKER_PROGRESS",
]

from typing import Generator, MutableMapping, Any

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.features import FEATURES


DOCKER_PROGRESS = [
    "auto",
    "quiet",
    "plain",
    "tty",
    "rawjson",
][2]


DOCKER_CONFIG = DockerConfig.LOCAL_HARBOR
DOCKER_USE_CACHE_GLOBAL = False
DOCKER_USE_CACHE_BASE = DOCKER_USE_CACHE_GLOBAL or False
PREFIX_COMPOSE_SCOPE = "ComposeScope"


from OpenStudioLandscapes.engine.compose_scopes.default import constants as constants_compose

GROUP_COMPOSE= constants_compose.GROUP
KEY_COMPOSE = constants_compose.KEY
ASSET_HEADER_COMPOSE = constants_compose.ASSET_HEADER
ENVIRONMENT_COMPOSE = constants_compose.ENVIRONMENT


from OpenStudioLandscapes.engine.compose_scopes.license_server import constants as constants_compose_license_server

GROUP_COMPOSE_LICENSE_SERVER= constants_compose_license_server.GROUP
KEY_COMPOSE_LICENSE_SERVER = constants_compose_license_server.KEY
ASSET_HEADER_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ASSET_HEADER
ENVIRONMENT_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ENVIRONMENT


from OpenStudioLandscapes.engine.compose_scopes.worker import constants as constants_compose_worker

GROUP_COMPOSE_WORKER= constants_compose_worker.GROUP
KEY_COMPOSE_WORKER = constants_compose_worker.KEY
ASSET_HEADER_COMPOSE_WORKER = constants_compose_worker.ASSET_HEADER
ENVIRONMENT_COMPOSE_WORKER = constants_compose_worker.ENVIRONMENT


GROUP_BASE_ENV = "OpenStudioLandscapes_Env"
KEY_BASE_ENV = [GROUP_BASE_ENV]

ASSET_HEADER_BASE_ENV = {
    "group_name": GROUP_BASE_ENV,
    "key_prefix": KEY_BASE_ENV,
}


GROUP_BASE = "OpenStudioLandscapes_Base"
KEY_BASE = [GROUP_BASE]

ASSET_HEADER_BASE = {
    "group_name": GROUP_BASE,
    "key_prefix": KEY_BASE,
}


GROUP_LANDSCAPE_MAP = "Landscape_Map"
KEY_LANDSCAPE_MAP = [GROUP_LANDSCAPE_MAP]

ASSET_HEADER_LANDSCAPE_MAP = {
    "group_name": GROUP_LANDSCAPE_MAP,
    "key_prefix": KEY_LANDSCAPE_MAP,
}

# BASE_CONFIGS = {
#     "ENVIRONMENT_BASE": {
#         "GIT_ROOT": pathlib.Path("{GIT_ROOT}"),
#         # Todo
#         #  - [ ] Move CONFIGS_ROOT to individual modules
#         "DOT_LANDSCAPES": pathlib.Path("{GIT_ROOT}", ".landscapes"),
#         "DOT_FEATURES": pathlib.Path("{GIT_ROOT}", ".features"),
#         "CONFIGS_ROOT": pathlib.Path(
#             git_root,
#             "configs",
#         ).as_posix(),
#         "AUTHOR": "michimussato@gmail.com",
#         "CREATED_BY": str(getpass.getuser()),
#         "CREATED_ON": str(socket.gethostname()),
#         "CREATED_AT": str(datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")),
#         "TIMEZONE": "Europe/Zurich",
#         # "IMAGE_PREFIX": "michimussato",
#         # Todo:
#         #  - [ ] Where is this being used?
#         "DEFAULT_CONFIG_DBPATH": "/data/configdb",
#         "ROOT_DOMAIN": "farm.evil",
#         # https://vfxplatform.com/
#         "PYTHON_MAJ": "3",
#         "PYTHON_MIN": "11",
#         "PYTHON_PAT": "11",
#     }
# }["ENVIRONMENT_BASE"]


@asset(
    **ASSET_HEADER_BASE_ENV,
    description="",
)
def constants_base(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    """ """

    _constants = {
        "DOCKER_USE_CACHE_BASE": DOCKER_USE_CACHE_BASE,
        "DOCKER_USE_CACHE_GLOBAL": DOCKER_USE_CACHE_GLOBAL,
        "ASSET_HEADER_BASE": ASSET_HEADER_BASE,
    }

    yield Output(_constants)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_constants),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
    description="",
    name="FEATURES",
)
def features(
    context: AssetExecutionContext,
) -> Generator[Output[dict] | AssetMaterialization | Any, None, None]:
    """ """

    global FEATURES

    yield Output(FEATURES)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(FEATURES),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
    description="",
    name="DOCKER_CONFIG",
)
def docker_config(
    context: AssetExecutionContext,
) -> Generator[Output[DockerConfig] | AssetMaterialization | Any, None, None]:
    """ """

    global DOCKER_CONFIG

    yield Output(DOCKER_CONFIG)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "DOCKER_CONFIG": MetadataValue.text(DOCKER_CONFIG.name),
            "value": MetadataValue.json(DOCKER_CONFIG.value),
            "type": MetadataValue.text(str(type(DOCKER_CONFIG))),
        },
    )
