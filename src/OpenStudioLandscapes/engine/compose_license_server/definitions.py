from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose_license_server.assets
import OpenStudioLandscapes.engine.compose_license_server.constants

assets = load_assets_from_modules(modules=[OpenStudioLandscapes.engine.compose_license_server.assets])
constants = load_assets_from_modules([OpenStudioLandscapes.engine.compose_license_server.constants])


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
