from dagster import (
    Definitions,
    load_assets_from_modules,
)
from OpenStudioLandscapes_Deadline_10_2 import (
    assets as assets_Deadline_v10_2,
)

assets = load_assets_from_modules(
    modules=[assets_Deadline_v10_2],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
