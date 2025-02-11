from dagster import (
    Definitions,
    load_assets_from_modules,
    AutoMaterializePolicy,
    AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu import (
    assets as assets_Kitsu,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu import (
    sensors as sensors_Kitsu,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.Kitsu import (
    jobs as jobs_Kitsu,
)

assets = load_assets_from_modules(
    modules=[assets_Kitsu],
    auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
        AutoMaterializeRule.materialize_on_parent_updated(),
    )
)


defs = Definitions(
    assets=[
        *assets,
    ],
    jobs=[
        jobs_Kitsu.job_Kitsu,
    ],
    sensors=[
        sensors_Kitsu.sensor__Base__group_out,
        sensors_Kitsu.sensor__auto_materialize_Kitsu,
    ]
)
