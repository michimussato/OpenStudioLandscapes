from OpenStudioLandscapes.engine.base.configurable_resources.config_engine import config_ConfigEngineConfigurableResource
from OpenStudioLandscapes.engine.base.configurable_resources.env_resource import config_EnvConfigurableResource
from OpenStudioLandscapes.engine.base.configurable_resources.docker_resource import config_DockerConfigurableResource
from OpenStudioLandscapes.engine.compose_scopes.configurable_resources.config_compose_scope import (
    config_ConfigComposeScopeConfigurableResource,
)


configurable_resources_base = {
    "config_ConfigEngineConfigurableResource": config_ConfigEngineConfigurableResource,
    "config_EnvConfigurableResource": config_EnvConfigurableResource,
    "config_DockerConfigurableResource": config_DockerConfigurableResource,
    "config_ConfigComposeScopeConfigurableResource": config_ConfigComposeScopeConfigurableResource,
}
