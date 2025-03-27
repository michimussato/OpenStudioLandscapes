from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.harbor.assets
# import OpenStudioLandscapes.engine.constants

assets = load_assets_from_modules([OpenStudioLandscapes.engine.harbor.assets])
# constants = load_assets_from_modules([OpenStudioLandscapes.engine.constants])


defs = Definitions(
    assets=[
        *assets,
        # *constants,
    ],
)
