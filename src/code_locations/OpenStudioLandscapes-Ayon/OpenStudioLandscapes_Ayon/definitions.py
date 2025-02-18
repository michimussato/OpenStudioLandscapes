from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes_Ayon.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes_Ayon.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
