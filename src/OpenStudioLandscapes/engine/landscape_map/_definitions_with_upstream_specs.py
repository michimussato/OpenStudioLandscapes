from dagster import (
    Definitions,
)

from OpenStudioLandscapes.engine.landscape_map.definitions import assets_base, assets_external


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
