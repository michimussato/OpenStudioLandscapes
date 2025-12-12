import enum
import os
import pathlib
import re
from importlib.metadata import Distribution
from typing import ClassVar, Dict, List

from dagster import (
    get_dagster_logger,
)
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    field_validator,
)

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


config_default = pathlib.Path(__file__).parent.joinpath("config_default.yml")
CONFIG_STR = config_default.read_text()


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
    docker_compose: pathlib.Path = Field(
        description="The path to the `docker-compose.yml` file.",
    )


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
        description="Run `docker` commands with the `--push` flag."
    )
    docker_pull: bool = Field(
        description="Run `docker` commands with the `--pull` flag."
    )
    docker_repository_name: str = Field(
        default="openstudiolandscapes", description="The registry repository name."
    )
    docker_registry_access: DockerRegistryAccess = Field(
        default="public",
        examples=["public", "private"],
    )
    docker_registry_protocol: DockerRegistryProtocol = Field(
        default="https",
        examples=["http", "https"],
    )
    docker_registry_fqdn: str = Field(
        description="The fully qualified domain name of the Docker Registry server.",
    )
    docker_registry_port: PositiveInt = Field(
        default=5000,
        description="The port the Docker Registry server is listening on.",
    )
    docker_registry_username: str = Field(
        description="The username of the Docker registry."
    )
    # Todo: docker_registry_password: SecretStr = Field(description="The password of the Docker registry.")
    #  Error:
    #  $ /usr/local/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-12-06-12-17-15-0a7941b92f824ef49f91c51870d89728/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json push registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_base_build_docker_image:2025-12-06-12-17-15-0a7941b92f824ef49f91c51870d89728
    #  The push refers to repository [registry.openstudiolandscapes.lan:5000/openstudiolandscapes/openstudiolandscapes_base_build_docker_image]
    #  f63ce67a7c61: Preparing
    #  f570bf7dffd1: Waiting
    #  190c42798dae: Waiting
    #  16035682a394: Waiting
    #  c8fa3aa32373: Waiting
    #  37f6c938862f: Waiting
    #  3713e6602b1c: Waiting
    #  5f70bf18a086: Waiting
    #  f414c81675d7: Waiting
    #  3a7a3de43f27: Waiting
    #  9b7574765262: Waiting
    #  e3a9ac4f35d1: Waiting
    #  814a4cc3f847: Waiting
    #  82ebc9df533a: Waiting
    #  04d8d56cf576: Waiting
    #  40f81487c646: Waiting
    #  5a1c3461da13: Waiting
    #  7db9cbeb8f44: Waiting
    #  46297afc02d3: Waiting
    #  475e9b631c20: Waiting
    #  ba5b5fb59128: Waiting
    #  ca51a7a2856a: Waiting
    #  dc863ccfdead: Waiting
    #  85597d481860: Waiting
    #  93079f5ed46d: Waiting
    #  e94f415811a7: Waiting
    #  32e97507fefc: Waiting
    #  9a00c67ce6ea: Waiting
    #  12e839af3df7: Waiting
    #  c1a487dda8ca: Waiting
    #  a319b73b6720: Waiting
    #  23a30637df68: Waiting
    #  a2a119fe7b9c: Waiting
    #  904ab20e9bbc: Waiting
    #  b91b4f675656: Waiting
    #  d24a6c37ccbe: Waiting
    #  63856c8ccf1c: Waiting
    #  470b66ea5123: Waiting
    #  unauthorized: authentication required
    docker_registry_password: str = Field(
        description="The password of the Docker registry."
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

    openstudiolandscapes__docker_config: DockerConfigModel = Field()

    # this initilizes a 'GIT_ROOT' by the config.yml
    # not sure yet if this is really necessary.
    openstudiolandscapes__repository_root: pathlib.Path = Field(
        default=pathlib.Path(
            os.environ.get(
                "OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT",
                default="~/git/repos/OpenStudioLandscapes",
            )
        )
    )

    # This has to be set via `OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT`
    # openstudiolandscapes__configstore_root: pathlib.Path = Field(
    #     # default=pathlib.Path(
    #     #     os.environ.get(
    #     #         "OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
    #     #         default="~/.config/OpenStudioLandscapes/config-store",
    #     #     )
    #     # )
    # )

    openstudiolandscapes__domain_lan: str = Field(
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__DOMAIN_LAN",
            default="openstudiolandscapes.lan",
        )
    )

    # openstudiolandscapes__domain_wan: Union[str, None] = os.environ.get(
    #     "OPENSTUDIOLANDSCAPES__DOMAIN_WAN",
    #     default=None,
    # )

    # openstudiolandscapes__domain_wan: str = "openstudiolandscapes.cloud-ip.cc"

    # openstudiolandscapes__su_method: str

    # openstudiolandscapes__docker_config: str  # should be DockerConfig
    #
    # openstudiolandscapes__attach_pangolin_site_to_compose_scope: bool

    # @field_validator("openstudiolandscapes__repository_root")
    # @classmethod
    # def ensure_valid__openstudiolandscapes__repository_root(cls, value: pathlib.Path):
    #     _value = value.expanduser()
    #     if not _value.exists():
    #         # Todo:
    #         #  - [ ] is_absolute()?
    #         #  - [ ] resolve()?
    #         # Create directory
    #         _value.mkdir(parents=True, exist_ok=True)
    #     if not _value.is_dir():
    #         raise ValueError(
    #             "`openstudiolandscapes__repository_root` is not a valid directory."
    #         )
    #     return value

    # @field_validator("openstudiolandscapes__configstore_root")
    # @classmethod
    # def ensure_valid__openstudiolandscapes__configstore_root(cls, value: pathlib.Path):
    #     _value = value.expanduser().resolve()
    #     if not _value.exists():
    #         # Create directory
    #         _value.mkdir(parents=True, exist_ok=True)
    #     if not _value.is_dir():
    #         raise ValueError(
    #             "`openstudiolandscapes__configstore_root` is not a valid directory."
    #         )
    #     return value


# This is the Feature Base Model
# DO NOT INSTANCE THIS DIRECTLY
# use Config Subclass instead
class FeatureBaseModel(BaseModel):
    """
    Base class for the Feature Config.

    All features inherit from this class.

    Concept is described here:
    - https://stackoverflow.com/a/50099920/2207196

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
            OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT
            .expanduser()
            .joinpath(
                self.feature_name,
                "config.yml",
            )
        )
        ret.parent.mkdir(parents=True, exist_ok=True)
        return ret

    # Automatic registration
    # - https://labex.io/tutorials/python-how-to-implement-automatic-registration-437881
    enabled: bool = Field(
        default=True,
        description="Whether the Feature is enabled or not.",
    )
    compose_scope: str = Field(
        default="default",
        examples=["default", "license_server", "worker"],
    )
    feature_name: str = Field(
        description="The name of the feature.",
        examples=["OpenStudioLandscapes-Kitsu", "OpenStudioLandscapes-VERT"],
        frozen=True,
    )
    group_name: str = Field(
        frozen=True,
    )

    @field_validator("group_name")
    @classmethod
    def validate(cls, value: str) -> str:
        # Methods:
        # - https://blog.finxter.com/5-best-ways-to-replace-a-list-of-characters-in-a-string-with-python/
        chars_to_replace = " .,-"
        replace_with = "_"

        regex_pattern = f"[{chars_to_replace}]"
        transformed_value = re.sub(regex_pattern, replace_with, value)
        return transformed_value.lower()

    key_prefixes: List[str] = Field()
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

    # dependencies: List[str] = Field(examples=["OpenStudioLandscapes-Kitsu"])
    definitions: str = Field(
        description="The path to the `definitions.py` file.",
        examples=[
            "OpenStudioLandscapes.Kitsu.definitions",
        ],
    )
