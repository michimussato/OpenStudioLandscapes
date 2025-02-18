from dagster import (
    Definitions,
    load_assets_from_modules,
)

from OpenStudioLandscapes.open_studio_landscapes.base import assets as assets_base


assets_base = load_assets_from_modules([assets_base])


defs = Definitions(
    assets=[
        *assets_base,
    ],
)
