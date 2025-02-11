from dagster import (
    Definitions,
    load_assets_from_modules,
    AutoMaterializePolicy,
    AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster import (
    assets as assets_Dagster,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster import (
    sensors as sensors_Dagster,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.Dagster import (
    jobs as jobs_Dagster,
)

assets = load_assets_from_modules(
    modules=[assets_Dagster],
    auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
        AutoMaterializeRule.materialize_on_parent_updated(),
    )
)


defs = Definitions(
    assets=[
        *assets,
    ],
    jobs=[
        jobs_Dagster.job_Dagster,
    ],
    sensors=[
        sensors_Dagster.sensor__Base__group_out,
        sensors_Dagster.sensor__auto_materialize_Dagster,
    ]
)
