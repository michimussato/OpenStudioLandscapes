from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu.assets import group_in

job_Kitsu = define_asset_job("job_Kitsu", [group_in])
