from OpenStudioLandscapes.engine.base.configurable_resources.env_resource import (
    config_EnvConfigurableResource,
)
from OpenStudioLandscapes.engine.base.configurable_resources.rez_resource import (
    config_RezConfigurableResource,
)
from OpenStudioLandscapes.engine.base.configurable_resources.docker_registry_resource import (
    config_DockerRegistryConfigurableResource,
)
from OpenStudioLandscapes.engine.base.configurable_resources.docker_resource import (
    config_DockerConfigurableResource,
)
from OpenStudioLandscapes.engine.base.configurable_resources.config_engine import (
    config_ConfigEngineConfigurableResource,
)


configurable_resources_base = {
    "config_EnvConfigurableResource": config_EnvConfigurableResource,
    "config_RezConfigurableResource": config_RezConfigurableResource,
    "config_DockerRegistryConfigurableResource": config_DockerRegistryConfigurableResource,
    "config_DockerConfigurableResource": config_DockerConfigurableResource,
    "config_ConfigEngineConfigurableResource": config_ConfigEngineConfigurableResource,
}
