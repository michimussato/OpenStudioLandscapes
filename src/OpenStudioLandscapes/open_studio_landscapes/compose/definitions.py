from dagster import (
    Definitions,
    load_assets_from_modules,
    AutoMaterializePolicy,
    AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.compose import (
    assets as assets_compose,
)
from OpenStudioLandscapes.open_studio_landscapes.compose import (
    sensors as sensors_compose,
)

from OpenStudioLandscapes.open_studio_landscapes.compose import (
    jobs as jobs_compose,
)

assets = load_assets_from_modules(
    modules=[assets_compose],
    # auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
    #     AutoMaterializeRule.materialize_on_parent_updated(),
    # )
)


defs = Definitions(
    assets=[
        *assets,
    ],
    jobs=[
        jobs_compose.job_compose,
    ],
    sensors=[
        # sensors_compose.sensor__Base__group_out,
        sensors_compose.sensor__Ayon__group_out,
        sensors_compose.sensor__Dagster__group_out,
        sensors_compose.sensor__filebrowser__group_out,
        sensors_compose.sensor__Grafana__group_out,
        sensors_compose.sensor__Kitsu__group_out,
        sensors_compose.sensor__LikeC4__group_out,
        # sensors_compose.sensor__auto_materialize_compose,
    ]
)


# from dagster import (
#     Definitions,
#     load_assets_from_modules,
#     # AutoMaterializePolicy,
#     # AutoMaterializeRule,
# )
# from OpenStudioLandscapes.open_studio_landscapes.compose import (
#     assets as assets_compose,
# )
# from OpenStudioLandscapes.open_studio_landscapes.compose import (
#     sensors as sensors_compose,
# )
#
# from OpenStudioLandscapes.open_studio_landscapes.compose import (
#     jobs as jobs_compose,
# )
#
# # from OpenStudioLandscapes.open_studio_landscapes.base import assets as assets_base
# # from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2 import assets as assets_Deadline_v10_2
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon import assets as assets_Ayon
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster import assets as assets_Dagster
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser import assets as assets_filebrowser
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana import assets as assets_Grafana
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu import assets as assets_Kitsu
# # from OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4 import assets as assets_LikeC4
#
#
#
# assets = load_assets_from_modules(
#     modules=[
#         assets_compose,
#         # assets_base,
#         # assets_Deadline_v10_2,
#         # assets_Ayon,
#         # assets_Dagster,
#         # assets_filebrowser,
#         # assets_Grafana,
#         # assets_Kitsu,
#         # assets_LikeC4,
#     ],
#     # auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
#     #     AutoMaterializeRule.materialize_on_parent_updated(),
#     # )
# )
#
#
# defs = Definitions(
#     assets=[
#         *assets,
#     ],
#     jobs=[
#         jobs_compose.job_compose,
#     ],
#     sensors=[
#         sensors_compose.sensor__Materialize__Compose_inputs,
#         # sensors_compose.sensor__Base__group_out,
#         # sensors_compose.sensor__Ayon__group_out,
#         # sensors_compose.sensor__Dagster__group_out,
#         # sensors_compose.sensor__filebrowser__group_out,
#         # sensors_compose.sensor__Grafana__group_out,
#         # sensors_compose.sensor__Kitsu__group_out,
#         # sensors_compose.sensor__LikeC4__group_out,
#         # # sensors_compose.sensor__auto_materialize_compose,
#     ]
# )
