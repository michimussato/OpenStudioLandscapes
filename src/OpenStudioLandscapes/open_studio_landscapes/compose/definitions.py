from dagster import (
    Definitions,
    load_assets_from_modules,
)
from OpenStudioLandscapes.open_studio_landscapes.compose import (
    assets as assets_compose,
)


assets = load_assets_from_modules(
    modules=[assets_compose],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
