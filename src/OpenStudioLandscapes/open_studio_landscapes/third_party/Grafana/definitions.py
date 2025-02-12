from dagster import (
    Definitions,
    load_assets_from_modules,
    # AutoMaterializePolicy,
    # AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana import (
    assets as assets_Grafana,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana import (
    sensors as sensors_Grafana,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.Grafana import (
    jobs as jobs_Grafana,
)

assets = load_assets_from_modules(
    modules=[assets_Grafana],
    # auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
    #     AutoMaterializeRule.materialize_on_parent_updated(),
    # )
)


defs = Definitions(
    assets=[
        *assets,
    ],
    jobs=[
        jobs_Grafana.job_Grafana,
    ],
    sensors=[
        sensors_Grafana.sensor__Base__group_out,
        # sensors_Grafana.sensor__auto_materialize_Grafana,
    ]
)
