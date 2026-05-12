from dagster import (
    Definitions,
)

from OpenStudioLandscapes.engine.env.definitions import assets_base

assets_external = []


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
