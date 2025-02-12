from dagster import (
    Definitions,
    load_assets_from_modules,
    # AutoMaterializePolicy,
    # AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4 import (
    assets as assets_LikeC4,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4 import (
    sensors as sensors_LikeC4,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.LikeC4 import (
    jobs as jobs_LikeC4,
)

assets = load_assets_from_modules(
    modules=[assets_LikeC4],
    # auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
    #     AutoMaterializeRule.materialize_on_parent_updated(),
    # )
)


defs = Definitions(
    assets=[
        *assets,
    ],
    jobs=[
        jobs_LikeC4.job_LikeC4,
    ],
    sensors=[
        sensors_LikeC4.sensor__Base__group_out,
        # sensors_LikeC4.sensor__auto_materialize_LikeC4,
    ]
)
