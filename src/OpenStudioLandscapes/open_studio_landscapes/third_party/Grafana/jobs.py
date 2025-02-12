from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana.assets import group_in

job_Grafana = define_asset_job(
    name="job_Grafana",
    selection=[group_in],
)
