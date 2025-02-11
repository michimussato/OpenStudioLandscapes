from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster.assets import group_in

job_Dagster = define_asset_job("job_Dagster", [group_in])
