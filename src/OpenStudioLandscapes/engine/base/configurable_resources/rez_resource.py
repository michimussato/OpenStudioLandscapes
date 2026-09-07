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


class RezConfigurableResource(ConfigurableResource):

    rez_version: str = Field(
        default="3.3.0",
    )

    # Where to PUT packages TO
    REZ_LOCAL_PACKAGES_PATH: str = Field(
        # locally installed pkgs, not yet deployed
        default="~/packages",
        description="https://rez.readthedocs.io/en/stable/configuring_rez.html#local_packages_path",
    )

    REZ_RELEASE_PACKAGES_PATH: str = Field(
        # internally developed pkgs, deployed
        default="~/.rez/packages/int",
        description="https://rez.readthedocs.io/en/stable/configuring_rez.html#release_packages_path",
    )

    REZ_EXTERNAL_PACKAGES_PATH: str = Field(
        # external (3rd party) pkgs, such as houdini, boost
        default="~/.rez/packages/ext",
        description="This variable can't be specified directly. We use `REZ_PACKAGES_PATH` "
        "to add this to the lookup paths. For more info, see: "
        "https://rez.readthedocs.io/en/stable/configuring_rez.html#packages_path",
    )

    @property
    def REZ_PACKAGES_PATH(self) -> List[pathlib.Path]:
        # Resources (@computed_field):
        # - https://stackoverflow.com/a/76301965
        # - https://docs.pydantic.dev/2.7/concepts/fields/#the-computed_field-decorator
        # -> just property without computed_field is fine here.
        #    no need to serialize this member when dumping the model
        #    An example of a successful computed_field implementation
        #    can be found here:
        #    - [OpenStudioLandscapes-DagsterCodeLocation-JobProcessor](https://github.com/michimussato/OpenStudioLandscapes-DagsterCodeLocation-JobProcessor/blob/main/src/OpenStudioLandscapes/DagsterCodeLocation/JobProcessor/deadline_templates/plugins/houdini/__init__.py)
        paths_ = [
            pathlib.Path(self.REZ_LOCAL_PACKAGES_PATH),
            pathlib.Path(self.REZ_RELEASE_PACKAGES_PATH),
            pathlib.Path(self.REZ_EXTERNAL_PACKAGES_PATH),
        ]
        return paths_

    @property
    def REZ_PACKAGES_PATH_ENV(self) -> str:
        return ":".join(i.expanduser().as_posix() for i in self.REZ_PACKAGES_PATH)

    @property
    def REZ_PACKAGES_PATH_VOL(self) -> List[str]:
        return [
            f"{i.expanduser().as_posix()}:{i.expanduser().as_posix()}"
            for i in self.REZ_PACKAGES_PATH
        ]

    @property
    def REZ_ENVIRONMENT(self) -> Dict[str, str]:
        env = {
            "REZ_PACKAGES_PATH": self.REZ_PACKAGES_PATH_ENV,
            "REZ_LOCAL_PACKAGES_PATH": pathlib.Path(self.REZ_LOCAL_PACKAGES_PATH).expanduser().as_posix(),
            "REZ_RELEASE_PACKAGES_PATH": pathlib.Path(self.REZ_RELEASE_PACKAGES_PATH).expanduser().as_posix(),
        }
        return env

    apt_packages_rez: List[str] = Field(
        default=[
            # $ rez bundle bakes/my_bake.rxt bundles/bundle_from_my_bake
            # 11:34:58 INFO     Bundling /rez/bakes/my_bake.rxt into /rez/bundles/bundle_from_my_bake...
            # 11:34:58 WARNING  Could not patch 127 files: cannot find 'readelf' utility.
            "binutils"
        ],
        frozen=True,
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


config_RezConfigurableResource_yaml: pathlib.Path = get_absolute_config_path(dist_engine).joinpath("config_rez_resource.yml")


config_RezConfigurableResource_yaml.parent.mkdir(parents=True, exist_ok=True)
if not config_RezConfigurableResource_yaml.exists():
    dump_yaml(
        model_config=RezConfigurableResource(),
        file_path=config_RezConfigurableResource_yaml,
    )
_yaml: Dict = load_yaml(file_path=config_RezConfigurableResource_yaml)
json_str = json.dumps(_yaml, indent=2)
config_RezConfigurableResource: RezConfigurableResource = RezConfigurableResource.model_validate_json(json_str)
