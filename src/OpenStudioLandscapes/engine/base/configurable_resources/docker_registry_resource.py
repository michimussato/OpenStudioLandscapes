import os
import pathlib
import json
from importlib.metadata import Distribution
from typing import (
    Dict,
)

from pydantic import (
    Field,
    field_validator
)

from dagster import (
    ConfigurableResource,
)

from OpenStudioLandscapes.engine.discovery.discovery import (
    dump_yaml,
    load_yaml,
)

from OpenStudioLandscapes.engine import dist as dist_engine
from OpenStudioLandscapes.engine.logging.loggers import DISCOVERY_LOGGER as LOGGER
from OpenStudioLandscapes.engine.config.models import (
    DockerRegistryAccess,
    DockerRegistryProtocol,
)


class DockerRegistryConfigurableResource(ConfigurableResource):
    """
    A current, valid DockerConfig:
    {
      "docker_push": true,
      "docker_registry_password": "registry-password",
      "docker_registry_port": "5000",
      "docker_registry_url": "registry.openstudiolandscapes.lan",
      "docker_registry_username": "registry-user",
      "docker_repository": "openstudiolandscapes",
      "docker_repository_type": "private",
      "docker_use_local": false
    }
    """

    docker_push: bool = Field(
        default=True, description="Run `docker` commands with the `--push` flag."
    )
    docker_pull: bool = Field(
        default=True, description="Run `docker` commands with the `--pull` flag."
    )
    docker_repository_name: str = Field(
        default="openstudiolandscapes", description="The registry repository name."
    )
    docker_registry_access: DockerRegistryAccess = Field(
        default=DockerRegistryAccess.public,
        examples=[i.name for i in DockerRegistryAccess],
    )
    docker_registry_protocol: DockerRegistryProtocol = Field(
        default=DockerRegistryProtocol.https,
        examples=[i.name for i in DockerRegistryProtocol],
    )
    docker_registry_fqdn: str = Field(
        default="registry.openstudiolandscapes.lan",
        description="The fully qualified domain name of the Docker Registry server.",
    )
    docker_registry_port: int = Field(
        default=5000,
        description="The port the Docker Registry server is listening on.",
    )
    docker_registry_username: str = Field(
        default="registry-user", description="The username of the Docker registry."
    )
    # Todo: docker_registry_password: SecretStr = Field(description="The password of the Docker registry.")
    #  Error:
    #  $ /usr/local/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-12-06-12-17-15-0a7941b92f824ef49f91c51870d89728/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json push registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-12-06-12-17-15-0a7941b92f824ef49f91c51870d89728
    #  The push refers to repository [registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_base_build_docker_image]
    #  f63ce67a7c61: Preparing
    #  f570bf7dffd1: Waiting
    #  [...]
    #  470b66ea5123: Waiting
    #  unauthorized: authentication required
    docker_registry_password: str = Field(
        default="registry-password", description="The password of the Docker registry."
    )

    @field_validator("docker_repository_name")
    @classmethod
    def lowercase_docker_repository_name(cls, value):
        # Do not:
        # - repeat special characters multiple times (like "__")
        # - use capitals in repository names
        return value.lower()


OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get(
        "OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
        # Todo:
        #  - [ ] if we launch OpenStudioLandscapes via `dagster dev`,
        #        this env var has not been set and will result in None -
        #        this is problematic. This is a workaround for now.
        #        -> see `dot_landscapes` asset for a better solution
        default="~/.config/OpenStudioLandscapes/config-store",
    )
).expanduser()


def get_absolute_config_path(
    dist: Distribution,
) -> pathlib.Path:
    """
    Get the absolute path of the configuration root.

    Returns:
        config_dir_path: pathlib.Path
    """

    LOGGER.debug(f"{dist.name = }")
    config_yml: pathlib.Path = OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.joinpath(
        dist.name,
        # "config.yml",
    )
    config_yml_expanded: pathlib.Path = config_yml.expanduser()
    LOGGER.debug(f"{config_yml = }")
    LOGGER.info(f"{config_yml_expanded = }")
    return config_yml_expanded


config_DockerRegistryConfigurableResource_yaml: pathlib.Path = get_absolute_config_path(dist_engine).joinpath("config_docker_registry_resource.yml")


config_DockerRegistryConfigurableResource_yaml.parent.mkdir(parents=True, exist_ok=True)
if not config_DockerRegistryConfigurableResource_yaml.exists():
    dump_yaml(
        model_config=DockerRegistryConfigurableResource(),
        file_path=config_DockerRegistryConfigurableResource_yaml,
    )
_yaml: Dict = load_yaml(file_path=config_DockerRegistryConfigurableResource_yaml)
json_str = json.dumps(_yaml, indent=2)
config_DockerRegistryConfigurableResource: DockerRegistryConfigurableResource = DockerRegistryConfigurableResource.model_validate_json(json_str)
