from dagster import (
    Definitions,
    load_assets_from_modules,
)

# @formatter:off
from OpenStudioLandscapes.open_studio_landscapes import assets as assets_base
from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2 import (
    assets as assets_Deadline_v10_2,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon import (
    assets as assets_Ayon,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster import (
    assets as assets_Dagster,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana import (
    assets as assets_Grafana,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu import (
    assets as assets_Kitsu,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4 import (
    assets as assets_LikeC4,
)
from OpenStudioLandscapes.open_studio_landscapes.Visualizer import (
    assets as assets_Visualizer,
)

# @formatter:on

assets_base = load_assets_from_modules([assets_base])
assets_10_2 = load_assets_from_modules([assets_Deadline_v10_2])

assets_visualizer = load_assets_from_modules([assets_Visualizer])

assets_ayon = load_assets_from_modules([assets_Ayon])
assets_grafana = load_assets_from_modules([assets_Grafana])
assets_dagster = load_assets_from_modules([assets_Dagster])
assets_kitsu = load_assets_from_modules([assets_Kitsu])
assets_likec4 = load_assets_from_modules([assets_LikeC4])

defs = Definitions(
    assets=[
        *assets_base,
        *assets_10_2,
        *assets_visualizer,
        *assets_ayon,
        *assets_grafana,
        *assets_dagster,
        *assets_kitsu,
        *assets_likec4,
    ],
)
