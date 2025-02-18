from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes_filebrowser.assets


assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes_filebrowser.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
