from dagster import (
    Definitions,
    load_assets_from_modules,
)
from Kitsu import (
    assets as assets_Kitsu,
)

assets = load_assets_from_modules(
    modules=[assets_Kitsu],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
