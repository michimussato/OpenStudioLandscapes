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
        sensors_compose.sensor__Base__group_out,
        sensors_compose.sensor__Ayon__group_out,
        sensors_compose.sensor__Dagster__group_out,
        sensors_compose.sensor__filebrowser__group_out,
        sensors_compose.sensor__Grafana__group_out,
        sensors_compose.sensor__Kitsu__group_out,
        sensors_compose.sensor__LikeC4__group_out,
        # sensors_compose.sensor__auto_materialize_compose,
    ]
)
