from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser.assets import group_in

job_filebrowser = define_asset_job(
    name="job_filebrowser",
    selection=[group_in],
)
