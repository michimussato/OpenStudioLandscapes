from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.base.assets

from OpenStudioLandscapes.engine.base.resources import resources

assets_base = load_assets_from_modules([OpenStudioLandscapes.engine.base.assets])


defs = Definitions(
    assets=[
        *assets_base,
    ],
    resources={
        **resources,
    }
)
