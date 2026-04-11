from dagster import (
    Definitions,
)

from OpenStudioLandscapes.engine.base.definitions import assets_base
from OpenStudioLandscapes.engine.env.assets import CONFIG_spec, env_spec

# from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE_ENV


assets_external = []


# env = AssetSpec(
#     key=AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"]),
#     group_name=ASSET_HEADER_BASE_ENV["group_name"],
#     description="Todo",
#     # dagster_type=dict,
# )
assets_external.append(env_spec)


# CONFIG = AssetSpec(
#     key=AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"]),
#     group_name=ASSET_HEADER_BASE_ENV["group_name"],
#     description="Todo",
# )
assets_external.append(CONFIG_spec)


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
