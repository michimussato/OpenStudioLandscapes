import enum
import os
import pathlib
import re
from importlib.metadata import Distribution
from typing import ClassVar, Dict, List

from dagster import (
    AssetIn,
    AssetKey,
    get_dagster_logger,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    field_validator,
)

from OpenStudioLandscapes.engine.config.str_gen import get_config_str

LOG = get_dagster_logger(__name__)

"""
Resources:
- https://app.studyraid.com/en/read/15002/518529/conditional-validation-based-on-other-fields
- https://thelinuxcode.com/work-with-pydantic-fields-detailed-examination/
- https://www.youtube.com/watch?v=Vj-iU-8_xLs
- https://www.youtube.com/watch?v=502XOB0u8OY
- https://docs.pydantic.dev/2.0/usage/models/
"""

# Todo
#  - [ ] Learn about serialization
#        - https://docs.pydantic.dev/latest/concepts/serialization/


# config_default = pathlib.Path(__file__).parent.joinpath("config_default.yml")
# CONFIG_STR = config_default.read_text()


class DockerRegistryProtocol(enum.StrEnum):
    http = "http"
    https = "https"


class DockerRegistryAccess(enum.StrEnum):
    public = "public"
    private = "private"


class ComposeScopeBaseModel(BaseModel):
    compose_scope: str = Field()
    attach_pangolin_site_to_compose_scope: bool = Field(
        default=False,
        description="Do you want the ComposeScope to dial in to " "a Pangolin site?",
    )
    attach_grafana_alloy_to_compose_scope: bool = Field(
        default=False,
        description="Do you want the ComposeScope to to collect Grafana metrics?",
    )

    docker_compose: pathlib.Path = Field(
        description="The path to the `docker-compose.yml` file.",
    )

    env: Dict = Field(
        default=None,
    )

    @property
    def docker_compose_expanded(self) -> pathlib.Path:
        ret = pathlib.Path(
            self.docker_compose.expanduser()
            .as_posix()
            .format(
                **self.env,
            )
        )
        return ret




class DockerRegistryConfig(BaseModel):
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
    docker_registry_port: PositiveInt = Field(
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


class DockerConfigModel(BaseModel):
    use_registry: bool = Field(
        default=False,
        description="Enable use of local or remote registry: push/pull images to registry like hub.docker.io.",
    )
    no_cache: bool = Field(
        default=False,
        description="Run `docker` commands with the `--no-cache` flag.",
    )
    docker_registry_config: DockerRegistryConfig = Field()


# class SudoMethod(enum.StrEnum):
#     # Todo
#     #  - [ ] implement `su`
#     #  - [ ] Also see OpenStudioLandscapes-Deadline-10-2 model
#     # SU = "su"
#     SUDO = "sudo"
#     PKEXEC = "pkexec"


class ConfigEngine(BaseModel):
    """
    An instance of this model has to be a singleton class.
    There can only be one ConfigEngine instance.

    References:
        - https://www.geeksforgeeks.org/python/singleton-pattern-in-python-a-complete-guide/
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "instance"):
            cls.instance = super(ConfigEngine, cls).__new__(cls)
        return cls.instance

    openstudiolandscapes__docker_config: DockerConfigModel = Field(
        default=DockerConfigModel(
            **{
                "use_registry": DockerConfigModel.model_fields["use_registry"].default,
                "no_cache": DockerConfigModel.model_fields["no_cache"].default,
                "docker_registry_config": DockerRegistryConfig(
                    **{
                        "docker_push": DockerRegistryConfig.model_fields[
                            "docker_push"
                        ].default,
                        "docker_pull": DockerRegistryConfig.model_fields[
                            "docker_pull"
                        ].default,
                        "docker_repository_name": DockerRegistryConfig.model_fields[
                            "docker_repository_name"
                        ].default,
                        "docker_registry_access": DockerRegistryConfig.model_fields[
                            "docker_registry_access"
                        ].default,
                        "docker_registry_protocol": DockerRegistryConfig.model_fields[
                            "docker_registry_protocol"
                        ].default,
                        "docker_registry_fqdn": DockerRegistryConfig.model_fields[
                            "docker_registry_fqdn"
                        ].default,
                        "docker_registry_port": DockerRegistryConfig.model_fields[
                            "docker_registry_port"
                        ].default,
                        "docker_registry_username": DockerRegistryConfig.model_fields[
                            "docker_registry_username"
                        ].default,
                        "docker_registry_password": DockerRegistryConfig.model_fields[
                            "docker_registry_password"
                        ].default,
                    },
                ),
            }
        ),
    )

    # # Todo:
    # #  - [ ] do we need this?
    # # this initilizes a 'GIT_ROOT' by the config.yml
    # # not sure yet if this is really necessary.
    # openstudiolandscapes__repository_root: pathlib.Path = Field(
    #     default=pathlib.Path(
    #         os.environ.get(
    #             "OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT",
    #             default="~/git/repos/OpenStudioLandscapes",
    #         )
    #     ),
    #     description="The full (local) path to the OpenStudioLandscapes Git repository.",
    # )

    # sudo_method: SudoMethod = Field(
    #     default=SudoMethod.PKEXEC,
    #     description=f"Setting up the MongoDB for {dist.name} requires you to "
    #     f"some commands to be executed as a privileged user. Usually, "
    #     f"`sudo` is fine and does not human interaction, however, "
    #     f"it requires the `sudo` password to exist in the `SUDO_PASS` "
    #     f"environment variable (`.env`). Same applies to `su`, while `su` "
    #     f"is available in Linux distros by default. "
    #     f"`pkexec` is *mostly* available on Linux systems with GUI's (Gnome, "
    #     f"KDE etc.) and is the cleanest way to grant `root` privileges. "
    #     f"It is does not require you to share your secrets in a "
    #     f"`.env` file as you will be prompted interactively to enter the "
    #     f"password before the commands are executed.",
    #     examples=[i.name for i in SudoMethod],
    # )

    openstudiolandscapes__domain_lan: str = Field(
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__DOMAIN_LAN",
            default="openstudiolandscapes.lan",
        )
    )


# This is the Feature Base Model
# DO NOT INSTANCE THIS DIRECTLY
# use Config Subclass instead
class FeatureBaseModel(BaseModel):
    """
    Base class for the Feature Config.

    All features inherit from this class.

    Concept is described here:
    - https://stackoverflow.com/a/50099920/2207196
    - https://labex.io/tutorials/python-how-to-implement-automatic-registration-437881

    ---

    An instance of this model has to be a singleton class.
    There can only be one ConfigEngine instance.

    References:
        - https://www.geeksforgeeks.org/python/singleton-pattern-in-python-a-complete-guide/
    """

    # ModuleType Fields:
    # pydantic.errors.PydanticSchemaGenerationError:
    #   Unable to generate pydantic-core schema for <class 'module'>.
    #   Set `arbitrary_types_allowed=True` in the model_config to
    #   ignore this error or implement `__get_pydantic_core_schema__`
    #   on your type to fully support it.
    model_config = ConfigDict(
        # This disables model checks for all fields.
        # More info here:
        # - https://stackoverflow.com/a/78379656/2207196
        arbitrary_types_allowed=True,
    )

    def __new__(cls, *args, **kwargs):
        if cls is FeatureBaseModel:
            # Prevent direct instantiation
            # References:
            # - https://stackoverflow.com/a/7990308/2207196
            raise TypeError(
                f"Do not instance this class directly. "
                f"Only children of '{cls.__name__}' may be instantiated"
            )
        if not hasattr(cls, "instance"):
            cls.instance = super(FeatureBaseModel, cls).__new__(cls)
        return cls.instance

    subclasses: ClassVar[Dict] = {}

    def __init_subclass__(cls, **kwargs):
        """

        This method is called when a subclass is instantiated.
        The instance will then be added to the base class subclasses list.

        Args:
            **kwargs:
        """
        super().__init_subclass__(**kwargs)
        # NOT UNIQUE: cls.__name__ = 'Config'
        # HENCE, USING: cls.feature_name = 'OpenStudioLandscapes-VERT'
        cls.subclasses[cls.feature_name] = cls

    def __repr__(self):
        return f"Feature({[f'{k}={v}' for k, v in self.__dict__.items()]})"

    def __str__(self):
        return f"{self.feature_name}"

    env: Dict = Field(
        default=None,
    )

    config_engine: ConfigEngine = Field(
        default=None,
    )

    # Forward Annotation
    # Reference:
    # - https://docs.pydantic.dev/latest/concepts/forward_annotations/
    config_parent: "FeatureBaseModel" = Field(
        default=None,
    )

    distribution: Distribution = Field(
        default=None,
    )

    # Dagster Attributes
    # Todo:
    #  - [ ] set group_name (if not defined) to feature_name
    #  - [ ] set key_prefixes (if not defined) to [feature_name]
    #  - [ ] validate using
    #        - `dagster._core.definitions.utils.VALID_NAME_REGEX`
    #        - `dagster._core.definitions.utils.VALID_NAME_REGEX_STR`
    #  - [ ] Replace Chars Methods:
    #        # - https://blog.finxter.com/5-best-ways-to-replace-a-list-of-characters-in-a-string-with-python/
    #        chars_to_replace = " .,-"
    #        replace_with = "_"
    #        regex_pattern = f"[{chars_to_replace}]"
    #        transformed_value = re.sub(regex_pattern, replace_with, value)
    group_name: str = Field(
        description="Dagster Group name. This will represent the group node name. "
        "See https://docs.dagster.io/api/dagster/assets for "
        "more information",
    )
    key_prefixes: List[str] = Field(
        description="Dagster Asset key prefixes. This will be reflected in the nesting "
        "(directory structure) of the Asset. "
        "See https://docs.dagster.io/api/dagster/assets for "
        "more information",
    )

    @property
    def dagster_compose_scope_in(self) -> AssetIn:
        default_name_feature_out = "feature_out_v2"
        ret = AssetIn(AssetKey([*self.key_prefixes, default_name_feature_out]))
        return ret

    # EXPANDABLE PATHS
    @property
    def config_file_path(self) -> pathlib.Path:
        OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT = pathlib.Path(
            os.environ.get(
                "OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
                default="~/.config/OpenStudioLandscapes/config-store",
            )
        )
        ret = pathlib.Path(
            OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT.expanduser().joinpath(
                self.feature_name,
                "config.yml",
            )
        )
        ret.parent.mkdir(parents=True, exist_ok=True)
        return ret

    # Todo
    #  - [ ] Maybe switch to disabled by default
    enabled: bool = Field(
        default=True,
        description="Whether the Feature is enabled or not.",
    )
    compose_scope: str = Field(
        default="default",
        examples=["default", "license_server", "worker"],
    )

    @field_validator("compose_scope")
    @classmethod
    def validate__compose_scope(cls, value: str) -> str:
        """
        ComposeScope names must be:
        - lowercase
        and may not contain
        - spaces
        - periods
        - commas
        - hyphens

        All illegal characters are replaced with underscores.

        Args:
            value: str

        Returns:
            str

        """
        # Methods:
        # - https://blog.finxter.com/5-best-ways-to-replace-a-list-of-characters-in-a-string-with-python/
        chars_to_replace = " .,-"
        replace_with = "_"

        regex_pattern = f"[{chars_to_replace}]"
        transformed_value = re.sub(regex_pattern, replace_with, value)
        return transformed_value.lower()

    # Todo
    #  - [ ] combine with key_prefixes/group_name?
    feature_name: str = Field(
        description="The name of the feature. It is derived from the "
        "`OpenStudioLandscapes.<Feature>.dist` attribute.",
        examples=["OpenStudioLandscapes-Kitsu", "OpenStudioLandscapes-VERT"],
        frozen=True,
    )

    docker_compose: pathlib.Path = Field(
        default=pathlib.Path(
            "{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml"
        ),
        description="The path to the `docker-compose.yml` file.",
    )

    @property
    def docker_compose_expanded(self) -> pathlib.Path:
        ret = pathlib.Path(
            self.docker_compose.expanduser()
            .as_posix()
            .format(
                **{
                    "FEATURE": self.feature_name,
                    **self.env,
                }
            )
        )
        return ret


CONFIG_STR = get_config_str(
    Config=ConfigEngine,
)
