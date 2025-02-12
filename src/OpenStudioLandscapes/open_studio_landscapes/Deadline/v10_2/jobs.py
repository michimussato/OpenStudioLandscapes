from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2.assets import group_in

job_Deadline_v10_2 = define_asset_job(
    name="job_Deadline_v10_2",
    selection=[group_in],
)
