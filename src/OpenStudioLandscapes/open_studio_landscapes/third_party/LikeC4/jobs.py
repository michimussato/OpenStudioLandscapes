from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4.assets import group_in

job_LikeC4 = define_asset_job(
    name="job_LikeC4",
    selection=[group_in],
)
