from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.compose_scopes.default.assets
import OpenStudioLandscapes.engine.compose_scopes.default.constants

assets = load_assets_from_modules(modules=[OpenStudioLandscapes.engine.compose_scopes.default.assets])
if bool(assets):
    constants = load_assets_from_modules([OpenStudioLandscapes.engine.compose_scopes.default.constants])
else:
    # This prevents constants asset from showing up it the
    # Dagster UI if the Feature itself is not enables/available.
    constants = []


defs = Definitions(
    assets=[
        *assets,
        *constants,
    ],
)
