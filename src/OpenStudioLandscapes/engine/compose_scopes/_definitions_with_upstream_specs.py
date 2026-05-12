from dagster import (
    Definitions,
)

from OpenStudioLandscapes.engine.compose_scopes.definitions import (
    assets_base,
    assets_external,
)

defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
