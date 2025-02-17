from dagster import (
    define_asset_job,
    AssetSelection,
)

from LikeC4.sensors import asset_to_watch


job_LikeC4 = define_asset_job(
    name="job_LikeC4",
    # Asset to trigger:
    # all in this code location minus the foreign one that was loaded into this gRPC
    selection=AssetSelection.all(include_sources=True) - AssetSelection.assets(asset_to_watch),
)
