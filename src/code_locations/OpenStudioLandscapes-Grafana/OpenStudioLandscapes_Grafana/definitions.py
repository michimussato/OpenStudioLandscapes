from dagster import (
    Definitions,
    load_assets_from_modules,
)
from OpenStudioLandscapes_Grafana import (
    assets as assets_Grafana,
)

assets = load_assets_from_modules(
    modules=[assets_Grafana],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
