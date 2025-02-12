from dagster import (
    define_asset_job,
    AssetSelection,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu.sensors import asset_to_watch


job_Kitsu = define_asset_job(
    name="job_Kitsu",
    # Asset to trigger:
    # all in this code location minus the foreign one that was loaded into this gRPC
    selection=AssetSelection.all(include_sources=True) - AssetSelection.assets(asset_to_watch),
)
