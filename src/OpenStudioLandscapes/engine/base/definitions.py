from dagster import (
    Definitions,
    load_assets_from_modules,
    AssetSpec,
    AssetKey,
)

import OpenStudioLandscapes.engine.base.assets
from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE_ENV

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


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
