from dagster import (
    define_asset_job,
)

# Asset to trigger:
from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana.assets import group_in

job_Grafana = define_asset_job("job_Grafana", [group_in])
