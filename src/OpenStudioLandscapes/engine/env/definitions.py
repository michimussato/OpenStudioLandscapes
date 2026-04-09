from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.env.assets

assets_base = load_assets_from_modules([OpenStudioLandscapes.engine.env.assets])


assets_external = []


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
