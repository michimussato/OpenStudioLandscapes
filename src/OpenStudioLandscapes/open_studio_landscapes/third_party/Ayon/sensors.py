from dagster import (
    AssetKey,
    RunRequest,
    asset_sensor,
    AutomationConditionSensorDefinition,
    AssetSelection,
    DefaultSensorStatus,
    SensorEvaluationContext,
)


from OpenStudioLandscapes.open_studio_landscapes.assets import KEY as KEY_BASE


# Trigger `my_job` when the `Base__group_out` asset is materialized
# Asset to watch:
asset_to_watch = [KEY_BASE, "group_out"]

@asset_sensor(
    asset_key=AssetKey(asset_to_watch),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_Ayon",
    minimum_interval_seconds=5,
)
def sensor__Base__group_out(
        context: SensorEvaluationContext,
):
    return RunRequest()


sensor__auto_materialize_Ayon = AutomationConditionSensorDefinition(
    "sensor__auto_materialize_Ayon",
    target=AssetSelection.all(include_sources=True),
    minimum_interval_seconds=15,
    default_status=DefaultSensorStatus.RUNNING,
)
