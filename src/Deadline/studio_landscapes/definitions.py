from dagster import (
    Definitions,
    load_assets_from_modules,
)
from Deadline.studio_landscapes import (
    assets,
    assets_10_2,
)
from Deadline.studio_landscapes.third_party import (
    ayon,
    dagster,
    kitsu,
    likec4,
)

assets_base = load_assets_from_modules([assets])
assets_10_2 = load_assets_from_modules([assets_10_2])

assets_ayon = load_assets_from_modules([ayon])
assets_dagster = load_assets_from_modules([dagster])
assets_kitsu = load_assets_from_modules([kitsu])
assets_likec4 = load_assets_from_modules([likec4])

defs = Definitions(
    assets=[
        *assets_base,
        *assets_10_2,
        *assets_ayon,
        *assets_dagster,
        *assets_kitsu,
        *assets_likec4,
    ],
)
