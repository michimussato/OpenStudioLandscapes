from dagster import (
    define_asset_job,
    AssetSelection,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon.sensors import asset_to_watch


job_Ayon = define_asset_job(
    name="job_Ayon",
    # Asset to trigger:
    # all in this code location minus the foreign one that was loaded into this gRPC
    selection=AssetSelection.all(include_sources=True) - AssetSelection.assets(asset_to_watch),
)
