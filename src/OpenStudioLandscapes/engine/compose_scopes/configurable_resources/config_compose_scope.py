import os
import pathlib
import json
from importlib.metadata import Distribution
from typing import (
    # List,
    Dict,
)

from pydantic import (
    Field,
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


class ConfigComposeScopeConfigurableResource(ConfigurableResource):

    # compose_scope: str = Field()

    attach_pangolin_site_to_compose_scope: bool = Field(
        default=bool(
            int(
                os.environ.get(
                    "OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE", 0
                )
            )
        ),
        description="Do you want the ComposeScope to dial in to a Pangolin Site?",
    )

    attach_grafana_alloy_to_compose_scope: bool = Field(
        default=bool(
            int(
                os.environ.get(
                    "OPENSTUDIOLANDSCAPES__ATTACH_GRAFANA_ALLOY_TO_COMPOSE_SCOPE", 0
                )
            )
        ),
        description="Do you want the ComposeScope to to populate Alloy metrics?",
    )
    grafana_alloy_listen_port_host: int = Field(
        default=12345,
        description="Do you want the ComposeScope to to populate Alloy metrics?",
    )
    grafana_alloy_listen_port_container: int = Field(
        default=12345,
        description="Do you want the ComposeScope to to populate Alloy metrics?",
    )
    grafana_alloy_listen_address: str = Field(
        default="0.0.0.0",
        description="Do you want the ComposeScope to to populate Alloy metrics?",
    )

    docker_compose: str = Field(
        description="The path to the `docker-compose.yml` file.",
        # This is only for dynamic usage so exclude=True
        exclude=True,
        default=pathlib.Path(
            "{DOT_LANDSCAPES}/{LANDSCAPE}/ComposeScope_{COMPOSE_SCOPE}/docker_compose/docker-compose.yml"
        ).as_posix(),
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


config_ConfigComposeScopeConfigurableResource_yaml: pathlib.Path = get_absolute_config_path(dist_engine).joinpath("config_compose_scope.yml")


config_ConfigComposeScopeConfigurableResource_yaml.parent.mkdir(parents=True, exist_ok=True)
if not config_ConfigComposeScopeConfigurableResource_yaml.exists():
    dump_yaml(
        model_config=ConfigComposeScopeConfigurableResource(),
        file_path=config_ConfigComposeScopeConfigurableResource_yaml,
    )
_yaml: Dict = load_yaml(file_path=config_ConfigComposeScopeConfigurableResource_yaml)
json_str = json.dumps(_yaml, indent=2)
config_ConfigComposeScopeConfigurableResource: ConfigComposeScopeConfigurableResource = ConfigComposeScopeConfigurableResource.model_validate_json(json_str)
