from dagster import (  # define_asset_job,; AssetSelection,
    Definitions,
    load_assets_from_modules,
)

import OpenStudioLandscapes.engine.env.assets

# from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE_ENV

assets_base = load_assets_from_modules([OpenStudioLandscapes.engine.env.assets])


# job_env = define_asset_job(
#     name=f"job_{ASSET_HEADER_BASE_ENV['group_name']}",
#     selection=AssetSelection.all(
#         # include_sources=True,
#     ),
# )


defs = Definitions(
    assets=[
        *assets_base,
    ],
    # jobs=[
    #     job_env,
    # ],
)
