from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon.assets import group_in

job_Ayon = define_asset_job(
    name="job_Ayon",
    selection=[group_in],
)
