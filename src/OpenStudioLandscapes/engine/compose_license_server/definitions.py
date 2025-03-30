from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose_license_server.assets

assets = load_assets_from_modules(
    modules=[OpenStudioLandscapes.engine.compose_license_server.assets],
)


defs = Definitions(
    assets=[
        *assets,
    ],
)
