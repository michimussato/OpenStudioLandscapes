import os

from OpenStudioLandscapes.engine.constants import (
    PREFIX_COMPOSE_SCOPE,
)
from OpenStudioLandscapes.engine.enums import *

COMPOSE_SCOPE = ComposeScope.DEFAULT

ATTACH_SITE_TO_COMPOSE_SCOPE = bool(
    int(os.environ.get("OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE", 0))
)


GROUP = f"{PREFIX_COMPOSE_SCOPE}_{str(COMPOSE_SCOPE)}"
KEY = [GROUP]

ASSET_HEADER = {
    "group_name": GROUP,
    "key_prefix": KEY,
    "compute_kind": "python",
}
