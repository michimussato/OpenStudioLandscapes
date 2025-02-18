from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes_LikeC4.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes_LikeC4.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
