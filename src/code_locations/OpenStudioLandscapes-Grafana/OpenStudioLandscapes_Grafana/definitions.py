from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes_Grafana.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes_Grafana.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
