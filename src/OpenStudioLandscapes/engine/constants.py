__all__ = [
    "PREFIX_COMPOSE_SCOPE",
    "ASSET_HEADER_BASE_ENV",
    "ASSET_HEADER_BASE",
    "ASSET_HEADER_LANDSCAPE_MAP",
    "ASSET_HEADER_DISTRIBUTABLE",
    "ASSET_HEADER_COMPOSE",
    "ASSET_HEADER_COMPOSE_LICENSE_SERVER",
    "ASSET_HEADER_COMPOSE_WORKER",
    "DOCKER_PROGRESS",
]

from typing import Any, Generator

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
    get_dagster_logger,
)

# used in OpenStudioLandscapes.engine.discovery.discovery
# DO NOT REMOVE
from OpenStudioLandscapes.engine.features import (
    FEATURES,
)

LOGGER = get_dagster_logger(__name__)

DOCKER_PROGRESS = [
    "auto",
    "quiet",
    "plain",
    "tty",
    "rawjson",
][2]


# Todo
#  - [ ] Find better config entry point
#        - Pydantic: https://medium.com/@jonathan_b/a-simple-guide-to-configure-your-python-project-with-pydantic-and-a-yaml-file-bef76888f366
#        - TypedDict:

PREFIX_COMPOSE_SCOPE = "ComposeScope"


from OpenStudioLandscapes.engine.compose_scopes.default import (
    constants as constants_compose,
)

GROUP_COMPOSE = constants_compose.GROUP
KEY_COMPOSE = constants_compose.KEY
ASSET_HEADER_COMPOSE = constants_compose.ASSET_HEADER


from OpenStudioLandscapes.engine.compose_scopes.license_server import (
    constants as constants_compose_license_server,
)

GROUP_COMPOSE_LICENSE_SERVER = constants_compose_license_server.GROUP
KEY_COMPOSE_LICENSE_SERVER = constants_compose_license_server.KEY
ASSET_HEADER_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ASSET_HEADER
# ENVIRONMENT_COMPOSE_LICENSE_SERVER = constants_compose_license_server.ENVIRONMENT


from OpenStudioLandscapes.engine.compose_scopes.worker import (
    constants as constants_compose_worker,
)

GROUP_COMPOSE_WORKER = constants_compose_worker.GROUP
KEY_COMPOSE_WORKER = constants_compose_worker.KEY
ASSET_HEADER_COMPOSE_WORKER = constants_compose_worker.ASSET_HEADER
# ENVIRONMENT_COMPOSE_WORKER = constants_compose_worker.ENVIRONMENT


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


GROUP_DISTRIBUTABLE = "Distributable"
KEY_DISTRIBUTABLE = [GROUP_DISTRIBUTABLE]

ASSET_HEADER_DISTRIBUTABLE = {
    "group_name": GROUP_DISTRIBUTABLE,
    "key_prefix": KEY_DISTRIBUTABLE,
}


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
