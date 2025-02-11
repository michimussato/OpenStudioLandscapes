from dagster import (
    AssetKey,
    RunRequest,
    asset_sensor,
    AutomationConditionSensorDefinition,
    AssetSelection,
    DefaultSensorStatus,
    SensorEvaluationContext,
    AssetMaterialization,
    Output,
)


# Trigger `my_job` when the `Base__group_out` asset is materialized
# Asset to watch:
asset_to_watch = ["Base", "group_out"]

@asset_sensor(
    asset_key=AssetKey(asset_to_watch),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_Deadline_10_2",
    minimum_interval_seconds=5,
    # required_resource_keys=
)
def sensor__Base__group_out(
        context: SensorEvaluationContext,
        asset_event,
):

    # materialization: AssetMaterialization = (
    #     asset_event.dagster_event.event_specific_data.materialization
    # )
    #
    # # output: Output = materialization.outputs
    #
    # context.log.info(f"{dir(asset_event) = }")
    # context.log.info(f"{dir(asset_event.asset_materialization) = }")
    # context.log.info(f"{dir(asset_event.asset_materialization.asset_key) = }")
    # context.log.info(f"{dir(asset_event.asset_observation) = }")
    # context.log.info(f"{dir(asset_event.dagster_event) = }")
    # context.log.info(f"{dir(asset_event.dagster_event.step_output_data) = }")
    # context.log.info(f"{dir(asset_event.dagster_event.event_specific_data) = }")
    #
    # context.log.info(f"{materialization = }")
    # context.log.info(f"{materialization.asset_key = }")
    # context.log.info(f"{materialization.metadata = }")
    #
    # context.log.info(f"{context = }")
    # context.log.info(f"{context.resources = }")
    # context.log.info(f"{context.resource_defs = }")
    # context.log.info(f"{dir(context) = }")
    return RunRequest()


sensor__auto_materialize_deadline_10_2 = AutomationConditionSensorDefinition(
    "sensor__auto_materialize_deadline_10_2",
    target=AssetSelection.all(include_sources=True),
    minimum_interval_seconds=15,
    default_status=DefaultSensorStatus.RUNNING,
)
