from dagster import (
    Definitions,
    load_assets_from_modules,
)
from OpenStudioLandscapes_filebrowser import (
    assets as assets_filebrowser,
)

assets = load_assets_from_modules(
    modules=[assets_filebrowser],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
