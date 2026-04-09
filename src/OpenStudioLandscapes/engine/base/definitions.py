from dagster import (
    Definitions,
    load_assets_from_modules,
    AssetSpec,
    AssetKey,
    define_asset_job,
    AssetSelection,
)

import OpenStudioLandscapes.engine.base.assets
from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE, ASSET_HEADER_BASE_ENV

assets_base = load_assets_from_modules(
    [OpenStudioLandscapes.engine.base.assets]
)


assets_external = []


env = AssetSpec(
    key=AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"]),
    group_name=ASSET_HEADER_BASE_ENV["group_name"],
    description="Todo",
)
assets_external.append(env)


CONFIG = AssetSpec(
    key=AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"]),
    group_name=ASSET_HEADER_BASE_ENV["group_name"],
    description="Todo",
)
assets_external.append(CONFIG)


job_base = define_asset_job(
    name=f"job_{ASSET_HEADER_BASE['group_name']}",
    selection=AssetSelection.all(
        # include_sources=True,
    ),
)


# job_env = define_asset_job(
#     name=f"job_{ASSET_HEADER_BASE_ENV['group_name']}",
#     # selection=AssetSelection.groups("OpenStudioLandscapes_Env"),
#     selection=AssetSelection.upstream_source_assets(),
# )


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
    jobs=[
        job_base,
        # job_env,
    ],
)
