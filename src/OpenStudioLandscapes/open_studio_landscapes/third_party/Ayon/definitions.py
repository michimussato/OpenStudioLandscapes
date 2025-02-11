from dagster import (
    Definitions,
    load_assets_from_modules,
    AutoMaterializePolicy,
    AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon import (
    assets as assets_Ayon,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon import (
    sensors as sensors_Ayon,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.Ayon import (
    jobs as jobs_Ayon,
)

assets = load_assets_from_modules(
    modules=[assets_Ayon],
    auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
        AutoMaterializeRule.materialize_on_parent_updated(),
    )
)


defs = Definitions(
    assets=[
        *assets,
    ],
    jobs=[
        jobs_Ayon.job_Ayon,
    ],
    sensors=[
        sensors_Ayon.sensor__Base__group_out,
        sensors_Ayon.sensor__auto_materialize_Ayon,
    ]
)
