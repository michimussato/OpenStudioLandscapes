from dagster import (
    AssetKey,
    RunRequest,
    asset_sensor,
    # AutomationConditionSensorDefinition,
    # AssetSelection,
    DefaultSensorStatus,
    SensorEvaluationContext,
)


from OpenStudioLandscapes.open_studio_landscapes.base.assets import KEY as KEY_BASE
from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon.assets import KEY as KEY_AYON
from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster.assets import KEY as KEY_DAGSTER
from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser.assets import KEY as KEY_FILEBROWSER
from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana.assets import KEY as KEY_GRAFANA
from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu.assets import KEY as KEY_KITSU
from LikeC4.assets import KEY as KEY_LIKEC4


# Trigger `my_job` when the `Base__group_out` asset is materialized
# Asset to watch:
asset_to_watch__Base = [KEY_BASE, "group_out"]
asset_to_watch__Ayon = [KEY_AYON, "group_out"]
asset_to_watch__Dagster = [KEY_DAGSTER, "group_out"]
asset_to_watch__filebrowser = [KEY_FILEBROWSER, "group_out"]
asset_to_watch__Grafana = [KEY_GRAFANA, "group_out"]
asset_to_watch__Kitsu = [KEY_KITSU, "group_out"]
asset_to_watch__LikeC4 = [KEY_LIKEC4, "group_out"]


# @asset_sensor(
#     asset_key=AssetKey(asset_to_watch__Base),
#     default_status=DefaultSensorStatus.RUNNING,
#     job_name="job_compose",
#     minimum_interval_seconds=5,
# )
# def sensor__Base__group_out(
#         context: SensorEvaluationContext,
# ):
#     return RunRequest()


@asset_sensor(
    asset_key=AssetKey(asset_to_watch__Ayon),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_compose",
    minimum_interval_seconds=5,
)
def sensor__Ayon__group_out(
        context: SensorEvaluationContext,
):
    return RunRequest()


@asset_sensor(
    asset_key=AssetKey(asset_to_watch__Dagster),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_compose",
    minimum_interval_seconds=5,
)
def sensor__Dagster__group_out(
        context: SensorEvaluationContext,
):
    return RunRequest()


@asset_sensor(
    asset_key=AssetKey(asset_to_watch__filebrowser),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_compose",
    minimum_interval_seconds=5,
)
def sensor__filebrowser__group_out(
        context: SensorEvaluationContext,
):
    return RunRequest()


@asset_sensor(
    asset_key=AssetKey(asset_to_watch__Grafana),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_compose",
    minimum_interval_seconds=5,
)
def sensor__Grafana__group_out(
        context: SensorEvaluationContext,
):
    return RunRequest()


@asset_sensor(
    asset_key=AssetKey(asset_to_watch__Kitsu),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_compose",
    minimum_interval_seconds=5,
)
def sensor__Kitsu__group_out(
        context: SensorEvaluationContext,
):
    return RunRequest()


@asset_sensor(
    asset_key=AssetKey(asset_to_watch__LikeC4),
    default_status=DefaultSensorStatus.RUNNING,
    job_name="job_compose",
    minimum_interval_seconds=5,
)
def sensor__LikeC4__group_out(
        context: SensorEvaluationContext,
):
    return RunRequest()


# sensor__auto_materialize_compose = AutomationConditionSensorDefinition(
#     "sensor__auto_materialize_compose",
#     target=AssetSelection.all(include_sources=True),
#     minimum_interval_seconds=15,
#     default_status=DefaultSensorStatus.RUNNING,
# )


# import copy
# import importlib
#
# from dagster import (
#     AssetKey,
#     RunRequest,
#     asset_sensor,
#     sensor,
#     AutomationConditionSensorDefinition,
#     AssetSelection,
#     DefaultSensorStatus,
#     SensorEvaluationContext,
#     Definitions,
# )
#
#
# # from OpenStudioLandscapes.open_studio_landscapes.base.assets import KEY as KEY_BASE
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon.assets import KEY as KEY_AYON
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster.assets import KEY as KEY_DAGSTER
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser.assets import KEY as KEY_FILEBROWSER
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana.assets import KEY as KEY_GRAFANA
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu.assets import KEY as KEY_KITSU
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4.assets import KEY as KEY_LIKEC4
# #
# #
# #
# # DEF_LOCS_THIRD_PARTY = [
# #     # "OpenStudioLandscapes.open_studio_landscapes.base",
# #     "OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2",
# #     "OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon",
# #     "OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster",
# #     "OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser",
# #     "OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana",
# #     "OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu",
# #     "OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4",
# # ]
# #
# # ins = list()
# #
# # definitions = list()
# #
# # for def_loc in DEF_LOCS_THIRD_PARTY:
# #     # load asset data from external code location into memory
# #     # and provide it as the Output of this asset
# #     # load_from = AssetKey([KEY_BASE, "group_out"])
# #     # Todo
# #     #  - [ ] get loc from code locations
# #     defs = importlib.import_module(f"{def_loc}.definitions").defs
# #     # df: dict = defs.load_asset_value(
# #     #     asset_key=load_from,
# #     #     instance=context.instance,
# #     # )
# #
# #     definitions.append(defs)
# #
# # assets = Definitions.merge(
# #     *definitions,
# # ).assets
#
#
#
# @sensor(
#     # job_name="job_compose",
#     asset_selection=AssetSelection.tag(
#         key="group_out",
#         value="third_party",
#         include_sources=True,
#     ),
#     default_status=DefaultSensorStatus.RUNNING,
#     minimum_interval_seconds=5,
# )
# def sensor__Materialize__Compose_inputs(
#         context: SensorEvaluationContext,
# ):
#     # if context.instance.get_scheduler_settings():
#     #     yield SkipReason("No new files found")
#     return RunRequest()
#
#
#
# # # Trigger `my_job` when the `Base__group_out` asset is materialized
# # # Asset to watch:
# # asset_to_watch__Base = [KEY_BASE, "group_out"]
# # asset_to_watch__Ayon = [KEY_AYON, "group_out"]
# # asset_to_watch__Dagster = [KEY_DAGSTER, "group_out"]
# # asset_to_watch__filebrowser = [KEY_FILEBROWSER, "group_out"]
# # asset_to_watch__Grafana = [KEY_GRAFANA, "group_out"]
# # asset_to_watch__Kitsu = [KEY_KITSU, "group_out"]
# # asset_to_watch__LikeC4 = [KEY_LIKEC4, "group_out"]
# #
# #
# # @asset_sensor(
# #     asset_key=AssetKey(asset_to_watch__Base),
# #     default_status=DefaultSensorStatus.RUNNING,
# #     job_name="job_compose",
# #     minimum_interval_seconds=5,
# # )
# # def sensor__Base__group_out(
# #         context: SensorEvaluationContext,
# # ):
# #     # if context.instance.get_scheduler_settings():
# #     #     yield SkipReason("No new files found")
# #     return RunRequest()
# #
# #
# # @asset_sensor(
# #     asset_key=AssetKey(asset_to_watch__Ayon),
# #     default_status=DefaultSensorStatus.RUNNING,
# #     job_name="job_compose",
# #     minimum_interval_seconds=5,
# # )
# # def sensor__Ayon__group_out(
# #         context: SensorEvaluationContext,
# # ):
# #     return RunRequest()
# #
# #
# # @asset_sensor(
# #     asset_key=AssetKey(asset_to_watch__Dagster),
# #     default_status=DefaultSensorStatus.RUNNING,
# #     job_name="job_compose",
# #     minimum_interval_seconds=5,
# # )
# # def sensor__Dagster__group_out(
# #         context: SensorEvaluationContext,
# # ):
# #     return RunRequest()
# #
# #
# # @asset_sensor(
# #     asset_key=AssetKey(asset_to_watch__filebrowser),
# #     default_status=DefaultSensorStatus.RUNNING,
# #     job_name="job_compose",
# #     minimum_interval_seconds=5,
# # )
# # def sensor__filebrowser__group_out(
# #         context: SensorEvaluationContext,
# # ):
# #     return RunRequest()
# #
# #
# # @asset_sensor(
# #     asset_key=AssetKey(asset_to_watch__Grafana),
# #     default_status=DefaultSensorStatus.RUNNING,
# #     job_name="job_compose",
# #     minimum_interval_seconds=5,
# # )
# # def sensor__Grafana__group_out(
# #         context: SensorEvaluationContext,
# # ):
# #     return RunRequest()
# #
# #
# # @asset_sensor(
# #     asset_key=AssetKey(asset_to_watch__Kitsu),
# #     default_status=DefaultSensorStatus.RUNNING,
# #     job_name="job_compose",
# #     minimum_interval_seconds=5,
# # )
# # def sensor__Kitsu__group_out(
# #         context: SensorEvaluationContext,
# # ):
# #     return RunRequest()
# #
# #
# # @asset_sensor(
# #     asset_key=AssetKey(asset_to_watch__LikeC4),
# #     default_status=DefaultSensorStatus.RUNNING,
# #     job_name="job_compose",
# #     minimum_interval_seconds=5,
# # )
# # def sensor__LikeC4__group_out(
# #         context: SensorEvaluationContext,
# # ):
# #     return RunRequest()
#
#
# # sensor__auto_materialize_compose = AutomationConditionSensorDefinition(
# #     "sensor__auto_materialize_compose",
# #     target=AssetSelection.all(include_sources=True),
# #     minimum_interval_seconds=15,
# #     default_status=DefaultSensorStatus.RUNNING,
# # )
