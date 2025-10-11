from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.resources.harbor.assets
from OpenStudioLandscapes.engine.resources.harbor.resources import resources

assets_base = load_assets_from_modules(
    [OpenStudioLandscapes.engine.resources.harbor.assets]
)


defs = Definitions(
    assets=[
        *assets_base,
    ],
    resources={
        **resources,
    },
)
