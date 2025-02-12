from dagster import (
    define_asset_job,
    AssetSelection,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster.sensors import asset_to_watch


job_Dagster = define_asset_job(
    name="job_Dagster",
    # Asset to trigger:
    # all in this code location minus the foreign one that was loaded into this gRPC
    selection=AssetSelection.all(include_sources=True) - AssetSelection.assets(asset_to_watch),
)
