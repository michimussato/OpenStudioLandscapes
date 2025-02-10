from dagster import (
    AssetKey,
    RunRequest,
    asset_sensor,
    AutomationConditionSensorDefinition,
    AssetSelection,
    DefaultSensorStatus,
    SensorEvaluationContext,
    AssetMaterialization
)


# Trigger `my_job` when the `Base__group_out` asset is materialized
# Asset to watch:
asset_to_watch = ["Base", "group_out"]

@asset_sensor(
    asset_key=AssetKey(asset_to_watch),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_Deadline_10_2",
    # required_resource_keys=
)
def sensor__Base__group_out(
        context: SensorEvaluationContext,
        asset_event,
):

    materialization: AssetMaterialization = (
        asset_event.dagster_event.event_specific_data.materialization
    )

    context.log.info(materialization)
    context.log.info(materialization.asset_key)
    context.log.info(materialization.metadata)

    context.log.info(context)
    context.log.info(context.resources)
    context.log.info(context.resource_defs)
    context.log.info(dir(context))
    return RunRequest()


sensor__auto_materialize_deadline_10_2 = AutomationConditionSensorDefinition(
    "sensor__auto_materialize_deadline_10_2",
    target=AssetSelection.all(include_sources=True),
    minimum_interval_seconds=15,
    default_status=DefaultSensorStatus.RUNNING,
)
