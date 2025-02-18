from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes_Dagster.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes_Dagster.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
