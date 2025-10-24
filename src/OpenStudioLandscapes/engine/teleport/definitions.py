import os

from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.teleport.assets

# import OpenStudioLandscapes.engine.teleport.constants

if os.environ["OPENSTUDIOLANDSCAPES__TELEPORT_ENABLE"].lower() == "true":
    assets = load_assets_from_modules(
        modules=[OpenStudioLandscapes.engine.teleport.assets],
    )

    # constants = load_assets_from_modules(
    #     modules=[OpenStudioLandscapes.engine.teleport.constants],
    # )
else:
    assets = []
    # constants = []


defs = Definitions(
    assets=[
        *assets,
        # *constants,
    ],
)
