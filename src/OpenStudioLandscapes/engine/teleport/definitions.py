import os

from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.teleport.assets

if os.environ["OPENSTUDIOLANDSCAPES__TELEPORT_ENABLE"].lower() == "true":
    assets = load_assets_from_modules(
        modules=[OpenStudioLandscapes.engine.teleport.assets],
    )
else:
    assets = []


defs = Definitions(
    assets=[
        *assets,
    ],
)
