from dagster import (
    Definitions,
)

from OpenStudioLandscapes.engine.vfx_reference.definitions import assets_base
from OpenStudioLandscapes.engine.env.assets import CONFIG, env
from OpenStudioLandscapes.engine.base.assets import docker_config_json


assets_external = []
assets_external.extend(env.specs)
assets_external.extend(CONFIG.specs)
assets_external.extend(docker_config_json.specs)


defs = Definitions(
    assets=[
        *assets_base,
        *assets_external,
    ],
)
