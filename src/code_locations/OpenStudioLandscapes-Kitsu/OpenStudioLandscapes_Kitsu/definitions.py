from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes_Kitsu.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes_Kitsu.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
