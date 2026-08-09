import os
import pathlib
import json
from importlib.metadata import Distribution
from typing import (
    Dict,
)

from pydantic import (
    Field,
    field_validator,
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


class EnvConfigurableResource(ConfigurableResource):
    # - [ ] how to make a dynamic property persistent?
    #   - [ ] keep current implemenation: via group_out_base
    #   - [ ] how to override base env with custom per feature values?
    # - [ ] generate if not configured via env var

    # Duplicated in ConfigEngineConfigurableResource
    AUTHOR: str = Field(
        default="michimussato@etik.com",
        description="The author of the OpenStudioLandscapes environment."
    )

    DOT_SHARED_VOLUMES: str = Field(
        default=".shared_volumes",
        description="The path to the .shared_volumes directory."
    )

    DOT_FEATURES: str = Field(
        default=pathlib.Path.cwd().joinpath(".features").expanduser().as_posix(),
        description="The path to the .features directory."
    )

    DOT_LANDSCAPES: str = Field(
        default=pathlib.Path.home().joinpath(".local", "share", "OpenStudioLandscapes", ".landscapes").expanduser().as_posix(),
        description="The path to the .landscapes directory."
    )

    LANDSCAPE: str = Field(
        default="MY_TEST_LANDSCAPE",
        description="The path to the .landscapes directory."
    )

    GIT_ROOT: str = Field(
        default=pathlib.Path.cwd().expanduser().as_posix(),
        description="The path to the OpenStudioLandscapes base directory."
    )

    @field_validator(
        "DOT_FEATURES",
        "DOT_LANDSCAPES",
        "GIT_ROOT",
    )
    @classmethod
    def convert_to_path(cls, value):
        return pathlib.Path(value).expanduser().as_posix()

    PYTHON_MAJ: str = Field(
        default="3",
        description="The Python version to use for the docker images."
    )

    PYTHON_MIN: str = Field(
        default="11",
        description="The Python version to use for the docker images."
    )

    PYTHON_PAT: str = Field(
        default="11",
        description="The Python version to use for the docker images."
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


config_EnvConfigurableResource_yaml: pathlib.Path = get_absolute_config_path(dist_engine).joinpath("config_env_resource.yml")


config_EnvConfigurableResource_yaml.parent.mkdir(parents=True, exist_ok=True)
if not config_EnvConfigurableResource_yaml.exists():
    dump_yaml(
        model_config=EnvConfigurableResource(),
        file_path=config_EnvConfigurableResource_yaml,
    )
_yaml: Dict = load_yaml(file_path=config_EnvConfigurableResource_yaml)
json_str = json.dumps(_yaml, indent=2)
config_EnvConfigurableResource: EnvConfigurableResource = EnvConfigurableResource.model_validate_json(json_str)
