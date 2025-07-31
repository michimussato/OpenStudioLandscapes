from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.distributable.assets

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.distributable.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
