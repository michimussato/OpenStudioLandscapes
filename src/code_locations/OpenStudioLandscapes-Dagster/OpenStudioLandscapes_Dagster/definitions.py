from dagster import (
    Definitions,
    load_assets_from_modules,
)
from OpenStudioLandscapes_Dagster import (
    assets as assets_Dagster,
)

assets = load_assets_from_modules(
    modules=[assets_Dagster],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
