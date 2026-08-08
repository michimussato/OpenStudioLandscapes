import os
import pathlib
import json
from importlib.metadata import Distribution
from typing import (
    List,
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
from OpenStudioLandscapes.engine.config.models import (
    SudoMethod,
)


class ConfigEngineConfigurableResource(ConfigurableResource):

    apt_packages_base: List[str] = Field(
        default=[
            "git",
            "ca-certificates",
            "htop",
            "file",
            "tzdata",
            "curl",
            # "less",
            "wget",
            "ffmpeg",
            "libegl1",
            "libsm6",
            "libglu1-mesa",
            "libxss1",
            "sudo",
            "neovim",
            # Untar xz file
            "xz-utils",
            # xvfb
            "xvfb",
            "xauth",
        ],
        frozen=True
    )

    apt_packages_build_python311: List[str] = Field(
        default=[
            "build-essential",
            "pkg-config",
            "zlib1g-dev",
            "libncurses5-dev",
            "libgdbm-dev",
            "libnss3-dev",
            "libssl-dev",
            "libreadline-dev",
            "libffi-dev",
            "libsqlite3-dev",
            "libbz2-dev",
            "iproute2",
            "liblzma-dev",
        ],
        frozen=True
    )

    pip_packages: List[str] = Field(
        default=[
            # Content moved to OpenStudioLandscapes.Dagster.assets.pip_packages
            # Todo:
            #  - [ ] enable OpenStudioLandscapes after making it public
            #  - [x] maybe move dagster stuff to dagster image?
        ],
        frozen=True,
    )

    openstudiolandscapes__domain_lan: str = Field(
        # Todo
        #  - [ ] use either env var or config. not both.
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__DOMAIN_LAN",
            default="openstudiolandscapes.lan",
        ),
    )

    openstudiolandscapes__human_readable_ids: bool = Field(
        default=True,
        description="Use `human-readable-id` (https://github.com/Karol-G/human-readable-id) to generate Landscape ID.",
    )

    sudo_method: SudoMethod = Field(
        default=SudoMethod.PKEXEC,  # Defaults to PKEXEC so that SUDO_PASS is always optional
        description=f"Usually, `sudo` is fine and does not require human interaction, however, "
        f"it requires the `sudo` password to exist in the `SUDO_PASS` "
        f"environment variable (`.env`). Same applies to `su` (not implemented), while `su` "
        f"is available in Linux distros by default. "
        f"`pkexec` is *mostly* available on Linux systems with GUI's (Gnome, "
        f"KDE etc.) and is the cleanest way to grant `root` privileges. "
        f"It is does not require you to share your secrets in a "
        f"`.env` file as you will be prompted interactively to enter the "
        f"password before the commands are executed. However, `pkexec` can only "
        f"be used when direct access to the operating system with a "
        f"GUI is available.",
        examples=[i.value for i in SudoMethod],
    )

    # This raises errors because the factory ConfigEngine is instanced directly
    # without being subclassed:
    # global_bind_volumes: List = Field(
    #     default_factory=list,
    # )
    global_bind_volumes: List[str] = []

    # This raises errors because the factory ConfigEngine is instanced directly
    # without being subclassed:
    # global_environment_variables: Dict = Field(
    #     default_factory=dict,
    # )
    global_environment_variables: Dict[str, str] = {}

    tz: str = Field(
        default="Europe/UTC",
    )

    # Duplicated in EnvConfigurableResource
    # Todo:
    #  - [ ] remove (used in compose scope?)
    author: str = Field(
        # Todo:
        #  - [ ] move to Env(BaseConfig)
        default="michimussato@etik.com",
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


config_ConfigEngineConfigurableResource_yaml: pathlib.Path = get_absolute_config_path(dist_engine).joinpath("config.yml")


config_ConfigEngineConfigurableResource_yaml.parent.mkdir(parents=True, exist_ok=True)
if not config_ConfigEngineConfigurableResource_yaml.exists():
    dump_yaml(
        model_config=ConfigEngineConfigurableResource(),
        file_path=config_ConfigEngineConfigurableResource_yaml,
    )
_yaml: Dict = load_yaml(file_path=config_ConfigEngineConfigurableResource_yaml)
json_str = json.dumps(_yaml, indent=2)
config_ConfigEngineConfigurableResource: ConfigEngineConfigurableResource = ConfigEngineConfigurableResource.model_validate_json(json_str)
