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
    DockerPullPolicy,
)


class DockerConfigurableResource(ConfigurableResource):
    use_registry: bool = Field(
        default=False,
        description="Enable use of local or remote registry: push/pull images to registry like hub.docker.io.",
    )
    no_cache: bool = Field(
        default=False,
        description="Run `docker` commands with the `--no-cache` flag.",
    )
    docker_pull_policy: DockerPullPolicy = Field(
        default=DockerPullPolicy.always,
        examples=[i.name for i in DockerPullPolicy],
        description="Run `docker` commands with the `--pull=<POLICY>` option.",
    )
    docker_compose_always_build: bool = Field(
        default=False,
        # examples=[i.name for i in DockerPullPolicy],
        description="Run `docker` commands with the `--build=<value>` option.",
    )
    docker_compose_force_recreate: bool = Field(
        default=False,
        # examples=[i.name for i in DockerPullPolicy],
        description="Run `docker` commands with the `--force-recreate=<value>` option.",
    )


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


config_DockerConfigurableResource_yaml: pathlib.Path = get_absolute_config_path(dist_engine).joinpath("config_docker_resource.yml")


config_DockerConfigurableResource_yaml.parent.mkdir(parents=True, exist_ok=True)
if not config_DockerConfigurableResource_yaml.exists():
    dump_yaml(
        model_config=DockerConfigurableResource(),
        file_path=config_DockerConfigurableResource_yaml,
    )
_yaml: Dict = load_yaml(file_path=config_DockerConfigurableResource_yaml)
json_str = json.dumps(_yaml, indent=2)
config_DockerConfigurableResource: DockerConfigurableResource = DockerConfigurableResource.model_validate_json(json_str)
