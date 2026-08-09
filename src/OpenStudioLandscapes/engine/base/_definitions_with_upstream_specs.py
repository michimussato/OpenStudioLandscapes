from dagster import (
    Definitions,
)

from OpenStudioLandscapes.engine.base.definitions import assets_base
from OpenStudioLandscapes.engine.env.assets import env

assets_external = []
assets_external.extend(env.specs)


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
