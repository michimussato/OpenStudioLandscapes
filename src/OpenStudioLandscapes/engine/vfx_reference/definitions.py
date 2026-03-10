from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.vfx_reference.assets

assets_base = load_assets_from_modules([OpenStudioLandscapes.engine.vfx_reference.assets])


defs = Definitions(
    assets=[
        *assets_base,
    ],
)
