from dagster import (
    Definitions,
    load_assets_from_modules,
)
from Ayon import (
    assets as assets_Ayon,
)

assets = load_assets_from_modules(
    modules=[assets_Ayon],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
