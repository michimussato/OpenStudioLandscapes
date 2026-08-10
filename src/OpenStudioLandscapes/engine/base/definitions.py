from dagster import (
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.base.assets
from OpenStudioLandscapes.engine.base.resources import configurable_resources_base

# from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE

assets_base = load_assets_from_modules([OpenStudioLandscapes.engine.base.assets])


# job_base = define_asset_job(
#     name=f"job_{ASSET_HEADER_BASE['group_name']}",
#     selection=AssetSelection.all(
#         # include_sources=True,
#     ),
# )


# job_env = define_asset_job(
#     name=f"job_{ASSET_HEADER_BASE_ENV['group_name']}",
#     # selection=AssetSelection.groups("OpenStudioLandscapes_Env"),
#     selection=AssetSelection.upstream_source_assets(),
# )


defs = Definitions(
    assets=[
        *assets_base,
    ],
    # jobs=[
    #     job_base,
    #     # job_env,
    # ],
    resources={
        **configurable_resources_base,
    },
)
