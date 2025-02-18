from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.open_studio_landscapes.base.assets


assets_base = load_assets_from_modules([OpenStudioLandscapes.open_studio_landscapes.base.assets])


defs = Definitions(
    assets=[
        *assets_base,
    ],
)
