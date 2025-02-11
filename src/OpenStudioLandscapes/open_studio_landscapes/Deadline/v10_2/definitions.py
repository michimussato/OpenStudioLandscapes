from dagster import (
    Definitions,
    load_assets_from_modules,
    AutoMaterializePolicy,
    AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2 import (
    assets as assets_Deadline_v10_2,
)
# from OpenStudioLandscapes.open_studio_landscapes import (
#     merge_compose as assets_merge_compose,
# )

from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2 import (
    sensors as sensors_Deadline_v10_2,
)

from OpenStudioLandscapes.open_studio_landscapes.Deadline.v10_2 import (
    jobs as jobs_Deadline_v10_2,
)

assets = load_assets_from_modules(
    modules=[assets_Deadline_v10_2],
    auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
        AutoMaterializeRule.materialize_on_parent_updated(),
    )
)

# assets_merge_compose = load_assets_from_modules([assets_merge_compose])

defs = Definitions(
    assets=[
        *assets,
        # *assets_merge_compose,
    ],
    jobs=[
        jobs_Deadline_v10_2.job_Deadline_v10_2,
    ],
    sensors=[
        sensors_Deadline_v10_2.sensor__Base__group_out,
        sensors_Deadline_v10_2.sensor__auto_materialize_Deadline_v10_2,
    ]
)
