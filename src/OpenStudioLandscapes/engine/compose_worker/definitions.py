from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose_worker.assets
import OpenStudioLandscapes.engine.compose_worker.constants

assets = load_assets_from_modules(modules=[OpenStudioLandscapes.engine.compose_worker.assets])
constants = load_assets_from_modules([OpenStudioLandscapes.engine.compose_worker.constants])


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
