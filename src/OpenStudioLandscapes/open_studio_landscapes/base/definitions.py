from dagster import (
    Definitions,
    load_assets_from_modules,
)

from OpenStudioLandscapes.open_studio_landscapes.base import assets as assets_base
# from OpenStudioLandscapes.open_studio_landscapes.compose import assets as assets_compose


assets_base = load_assets_from_modules([assets_base])
# assets_compose = load_assets_from_modules([assets_compose])

defs = Definitions(
    assets=[
        *assets_base,
        # *assets_compose,
    ],
)
