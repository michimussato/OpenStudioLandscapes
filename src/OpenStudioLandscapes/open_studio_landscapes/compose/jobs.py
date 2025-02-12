from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.compose.assets import group_in

job_compose = define_asset_job(
    name="job_compose",
    selection=[group_in],
)
