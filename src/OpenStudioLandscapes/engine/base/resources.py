from OpenStudioLandscapes.engine.base.configurable_resources.rez_resource import (
    config_RezConfigurableResource,
)
from OpenStudioLandscapes.engine.base.configurable_resources.docker_registry_resource import (
    config_DockerRegistryConfigurableResource,
)
from OpenStudioLandscapes.engine.base.configurable_resources.docker_resource import (
    config_DockerConfigurableResource,
)

configurable_resources_base = {
    "config_RezConfigurableResource": config_RezConfigurableResource,
    "config_DockerRegistryConfigurableResource": config_DockerRegistryConfigurableResource,
    "config_DockerConfigurableResource": config_DockerConfigurableResource,
}
