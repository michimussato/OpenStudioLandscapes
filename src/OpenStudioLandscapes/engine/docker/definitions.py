from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.docker.assets

assets_base = load_assets_from_modules([OpenStudioLandscapes.engine.docker.assets])


defs = Definitions(
    assets=[
        *assets_base,
    ],
)
