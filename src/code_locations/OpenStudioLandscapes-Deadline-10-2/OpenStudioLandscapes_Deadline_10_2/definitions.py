from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes_Deadline_10_2.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes_Deadline_10_2.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
