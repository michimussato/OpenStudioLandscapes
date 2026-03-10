__all__ = [
    "DAGSTER_DEFAULT_OUTPUT",
    "ConfigParent",
    "ASSET_HEADER_BASE_ENV",
    "ASSET_HEADER_VFX_PLATFORM",
    "ASSET_HEADER_BASE",
    "ASSET_HEADER_LANDSCAPE_MAP",
    "ASSET_HEADER_DISTRIBUTABLE",
    "DOCKER_PROGRESS",
]

from typing import Union

from dagster import get_dagster_logger
from dagster._core.definitions.utils import DEFAULT_OUTPUT as DAGSTER_DEFAULT_OUTPUT

LOGGER = get_dagster_logger(__name__)

from OpenStudioLandscapes.engine.config.models import FeatureBaseModel

ConfigParent: Union[None, FeatureBaseModel] = None

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


GROUP_VFX_PLATFORM = "OpenStudioLandscapes_VFX_Platform"
KEY_VFX_PLATFORM = [GROUP_VFX_PLATFORM]

ASSET_HEADER_VFX_PLATFORM = {
    "group_name": GROUP_VFX_PLATFORM,
    "key_prefix": KEY_VFX_PLATFORM,
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
