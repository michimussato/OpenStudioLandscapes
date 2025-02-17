from dagster import (
    Definitions,
    load_assets_from_modules,
)
from OpenStudioLandscapes_LikeC4 import (
    assets as assets_LikeC4,
)

assets = load_assets_from_modules(
    modules=[assets_LikeC4],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
