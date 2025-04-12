from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose_pi_hole.assets
import OpenStudioLandscapes.engine.compose_pi_hole.constants

assets = load_assets_from_modules([OpenStudioLandscapes.engine.compose_pi_hole.assets])
constants = load_assets_from_modules([OpenStudioLandscapes.engine.compose_pi_hole.constants])


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
