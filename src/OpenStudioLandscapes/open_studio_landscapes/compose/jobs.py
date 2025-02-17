from dagster import (
    define_asset_job,
    AssetSelection, AssetKey,
)

from OpenStudioLandscapes.open_studio_landscapes.base.assets import KEY as KEY_BASE
from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2.assets import KEY as KEY_DEADLINE
from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon.assets import KEY as KEY_AYON
from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster.assets import KEY as KEY_DAGSTER
from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser.assets import KEY as KEY_FILEBRWOSER
from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana.assets import KEY as KEY_GRAFANA
from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu.assets import KEY as KEY_KITSU
from LikeC4.assets import KEY as KEY_LIKEC4


job_compose = define_asset_job(
    name="job_compose",
    # Asset to trigger:
    # all in this code location minus the foreign one that was loaded into this gRPC
    selection=AssetSelection.all(include_sources=True)
              - AssetSelection.assets(
        AssetKey([KEY_BASE, "group_out"]),
        AssetKey([KEY_DEADLINE, "group_out"]),
        AssetKey([KEY_AYON, "group_out"]),
        AssetKey([KEY_DAGSTER, "group_out"]),
        AssetKey([KEY_FILEBRWOSER, "group_out"]),
        AssetKey([KEY_GRAFANA, "group_out"]),
        AssetKey([KEY_KITSU, "group_out"]),
        AssetKey([KEY_LIKEC4, "group_out"]),
    ),
)
