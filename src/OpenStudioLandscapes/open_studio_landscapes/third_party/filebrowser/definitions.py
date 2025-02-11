from dagster import (
    Definitions,
    load_assets_from_modules,
    AutoMaterializePolicy,
    AutoMaterializeRule,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser import (
    assets as assets_filebrowser,
)
from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser import (
    sensors as sensors_filebrowser,
)

from OpenStudioLandscapes.open_studio_landscapes.third_party.filebrowser import (
    jobs as jobs_filebrowser,
)

assets = load_assets_from_modules(
    modules=[assets_filebrowser],
    auto_materialize_policy=AutoMaterializePolicy.lazy().with_rules(
        AutoMaterializeRule.materialize_on_parent_updated(),
    )
)


defs = Definitions(
    assets=[
        *assets,
    ],
    jobs=[
        jobs_filebrowser.job_filebrowser,
    ],
    sensors=[
        sensors_filebrowser.sensor__Base__group_out,
        sensors_filebrowser.sensor__auto_materialize_filebrowser,
    ]
)
