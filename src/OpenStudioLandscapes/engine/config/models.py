import enum
import json
import os
import pathlib
import re
from importlib.metadata import Distribution
from typing import ClassVar, Dict, List
from types import ModuleType

import pydantic
import yaml
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


class DockerPullPolicy(enum.StrEnum):
    never = "never"
    missing = "missing"
    always = "always"


class BaseConfig(BaseModel):

    @classmethod
    def get_docs(cls) -> str:
        """
        Implementation based on
        https://trhallam.github.io/trhallam/blog/pydantic-yaml-config/#comments-for-repetitive-fields

        This is a naive approach but works for now.

        Examples:

            from OpenStudioLandscapes.engine.config.models import ConfigEngine as Config
            print(Config.get_docs())

            from OpenStudioLandscapes.Kitsu.config.models import Config
            print(Config.get_docs())


        Returns:
            str:

        """

        # # doc = []
        # class_name = cls.__name__
        # docs = f"# {''.rjust(len(class_name), '=')}\n"
        # docs += f"# {class_name}\n"
        # docs += f"# {''.rjust(len(class_name), '-')}\n"
        # docs += "# \n"
        # docs += "# Docstring:\n"
        # docs += "".join([f"# {l}\n" for l in textwrap.dedent(str(cls.__doc__)).split("\n")])
        # docs += "# \n\n"
        # fields = []

        LOG.info(f"{cls.model_fields = }")

        doc_str = str()

        field_k: str
        field_v: pydantic.FieldInfo

        for field_k, field_v in cls.model_fields.items():
            try:
                LOG.info(f"{field_k = }")
                LOG.info(f"{field_v.is_required() = }")
                # LOGGER.debug(f"Field name: {field_k}")

                # LOGGER.debug(f"\tValues specified in Config:")

                sub_class_required = field_v.is_required()
                sub_class_value = field_v.default
                sub_class_annotation = field_v.annotation
                sub_class_description = str(field_v.description)
                sub_class_examples = str(field_v.examples)
                # LOGGER.debug(f"\t\tType: {annotation}")
                # LOGGER.debug(f"\t\tValue: {sub_class_value}")
                # LOGGER.debug(f"\t\tDescription: {sub_class_description}")

                doc_str += f"# {''.rjust(len(field_k), '=')}\n"
                doc_str += f"# {field_k}\n"
                doc_str += f"# {''.rjust(len(field_k), '-')}\n"
                doc_str += f"#\n"
                doc_str += f"# Type: {sub_class_annotation}\n"

                base_class_value = ""

                if field_k in cls.__base__.model_fields:
                    # print(f"\tDefault Value: {Config.__base__.model_fields[field_k] = }")
                    base_class_required = cls.__base__.model_fields[
                        field_k
                    ].is_required()
                    base_class_value = cls.__base__.model_fields[field_k].default
                    # base_class_annotation = Config.__base__.model_fields[field_k].annotation
                    base_class_description = cls.__base__.model_fields[
                        field_k
                    ].description
                    # LOGGER.debug(f"\t\tType: {base_class_annotation}")
                    # LOGGER.debug(f"\t\tDefault Value: {base_class_value}")
                    # LOGGER.debug(f"\t\tDefault Description: {base_class_description}")

                    doc_str += (
                        f"# Base Class Info:\n"
                        f"#     Required:\n"
                        f"#         {base_class_required}\n"
                        f"#     Description:\n"
                        f"#         {base_class_description}\n"
                        f"#     Default value:\n"
                        f"#         {base_class_value}\n"
                    )

                doc_str += (
                    f"# Description:\n"
                    f"#     {sub_class_description}\n"
                    f"# Required:\n"
                    f"#     {sub_class_required}\n"
                    f"# Examples:\n"
                    f"#     {sub_class_examples}\n"
                )

                try:
                    if base_class_value == sub_class_value:
                        doc_str += f"\n\n"
                        continue

                except UnboundLocalError as e:
                    LOG.warning(f"{e}")

                # if isinstance(sub_class_value, PydanticUndefinedType):
                #     kv = {field_k: "<NOT SET> (CHANGE_ME)"}
                # else:
                if isinstance(sub_class_value, pydantic.BaseModel):
                    v = json.loads(
                        sub_class_value.model_dump_json(indent=2, fallback=str)
                    )
                else:
                    v = sub_class_value
                kv = {field_k: v}

                doc_str += f"{yaml.safe_dump(json.loads(json.dumps(kv, indent=2, default=str)))}\n\n"

            except Exception as e:
                LOG.error(f"{e}")
                raise Exception from e

        return doc_str.rstrip()  # strip trailing newlines


class ComposeScopeBaseModel(BaseConfig):

    compose_scope: str = Field()

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

    docker_compose: pathlib.Path = Field(
        description="The path to the `docker-compose.yml` file.",
        exclude=True,
    )

    env: Dict = Field(
        default=None,
    )

    # Forward Annotation
    # Reference:
    # - https://docs.pydantic.dev/latest/concepts/forward_annotations/
    config_engine: "ConfigEngine" = Field(
        default=None,
        exclude=True,
    )

    @property
    def docker_compose_expanded(self) -> pathlib.Path:
        ret = pathlib.Path(
            self.docker_compose.expanduser()  # pylint: disable=E1101
            .as_posix()
            .format(
                **self.env,
            )
        )
        return ret


class DockerRegistryConfig(BaseConfig):
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


class DockerConfigModel(BaseConfig):
    use_registry: bool = Field(
        default=False,
        description="Enable use of local or remote registry: push/pull images to registry like hub.docker.io.",
    )
    no_cache: bool = Field(
        default=False,
        description="Run `docker` commands with the `--no-cache` flag.",
    )
    docker_registry_config: DockerRegistryConfig = Field()
    docker_pull_policy: DockerPullPolicy = Field(
        default=DockerPullPolicy.always,
        examples=[i.name for i in DockerPullPolicy],
        description="Run `docker` commands with the `--pull=<POLICY>` option.",
    )


class RezConfigModel(BaseConfig):

    rez_version: str = Field(
        default="3.3.0",
    )

    # Where to PUT packages TO
    REZ_LOCAL_PACKAGES_PATH: pathlib.Path = Field(
        # locally installed pkgs, not yet deployed
        default=pathlib.Path("~/packages"),
        description="https://rez.readthedocs.io/en/stable/configuring_rez.html#local_packages_path",
    )

    REZ_RELEASE_PACKAGES_PATH: pathlib.Path = Field(
        # internally developed pkgs, deployed
        default=pathlib.Path("~/.rez/packages/int"),
        description="https://rez.readthedocs.io/en/stable/configuring_rez.html#release_packages_path",
    )

    REZ_EXTERNAL_PACKAGES_PATH: pathlib.Path = Field(
        # external (3rd party) pkgs, such as houdini, boost
        default=pathlib.Path("~/.rez/packages/ext"),
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
            self.REZ_LOCAL_PACKAGES_PATH,
            self.REZ_RELEASE_PACKAGES_PATH,
            self.REZ_EXTERNAL_PACKAGES_PATH,
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
            "REZ_LOCAL_PACKAGES_PATH": self.REZ_LOCAL_PACKAGES_PATH.expanduser().as_posix(),
            "REZ_RELEASE_PACKAGES_PATH": self.REZ_RELEASE_PACKAGES_PATH.expanduser().as_posix(),
        }
        return env

    apt_packages_rez: List = Field(
        default=[
            # $ rez bundle bakes/my_bake.rxt bundles/bundle_from_my_bake
            # 11:34:58 INFO     Bundling /rez/bakes/my_bake.rxt into /rez/bundles/bundle_from_my_bake...
            # 11:34:58 WARNING  Could not patch 127 files: cannot find 'readelf' utility.
            "binutils",
        ],
        frozen=True,
    )


class SudoMethod(enum.StrEnum):
    # Todo
    #  - [ ] implement `su`
    #  - [ ] Also see OpenStudioLandscapes ConfigEngine model
    # SU = "su"
    SUDO = "sudo"
    PKEXEC = "pkexec"


class ConfigEngine(BaseConfig):
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
        description="The Docker Configuration for OpenStudioLandscapes.",
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

    openstudiolandscapes__rez_config: RezConfigModel = Field(
        default=RezConfigModel(
            **{
                "deploy_rez": True,
                # The following has no effect here:
                # REZ_PACKAGES_PATH refers to a property, not a Field
                # Hence, model gets created using defaults for:
                # - REZ_LOCAL_PACKAGES_PATH
                # - REZ_RELEASE_PACKAGES_PATH
                # - REZ_EXTERNAL_PACKAGES_PATH
                # "REZ_PACKAGES_PATH": [
                #     pathlib.Path("~/rez/packages/local"),
                #     pathlib.Path("~/rez/packages/deployed/internal"),
                #     pathlib.Path("/data/share/rez-packages/packages"),
                # ],
            },
        ),
    )

    apt_packages_base: List = Field(
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
        frozen=True,
    )

    apt_packages_build_python311: List = Field(
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
        frozen=True,
    )

    pip_packages: List = Field(
        default=[
            # Content moved to OpenStudioLandscapes.Dagster.assets.pip_packages
            # Todo:
            #  - [ ] enable OpenStudioLandscapes after making it public
            #  - [x] maybe move dagster stuff to dagster image?
        ],
        frozen=True,
    )

    openstudiolandscapes__domain_lan: str = Field(
        default=os.environ.get(
            "OPENSTUDIOLANDSCAPES__DOMAIN_LAN",
            default="openstudiolandscapes.lan",
        )
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


# This is the Feature Base Model
# DO NOT INSTANCE THIS DIRECTLY
# use Config Subclass instead
class FeatureBaseModel(BaseConfig):
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
        default_factory=dict,
    )

    # This does not raise errors because each Feature subclasses this class.
    local_bind_volumes: List[str] = Field(
        default_factory=list,
        description="Here you can define Feature specific, arbitrary, absolute bind volume mappings.",
    )

    # This does not raise errors because each Feature subclasses this class.
    local_environment_variables: Dict[str, str] = Field(
        default_factory=dict,
        description="Here you can define Feature specific, arbitrary environment variables.",
    )

    config_engine: ConfigEngine = Field(
        default=None,
        # Exclude Field from Model Serialization
        exclude=True,
    )

    distribution: Distribution = Field(
        default=None,
        # Exclude Field from Model Serialization
        exclude=True,
    )

    # tz: str = Field(
    #     default="Europe/UTC",
    # )

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
            self.docker_compose.expanduser()  # pylint: disable=E1101
            .as_posix()
            .format(
                **{
                    "FEATURE": self.feature_name,
                    **self.env,
                }
            )
        )
        return ret


class OpenStudioLandscapesDiscoveredFeature(BaseModel):
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

    definitions: str = Field()
    definitions_object: ModuleType = Field(
        default=None,
    )

    models: str = Field()
    models_object: ModuleType = Field(
        default=None,
    )

    config: FeatureBaseModel = Field(
        default=None,
        # default_factory=FeatureBaseModel,
    )


# Todo:
#  - [ ] add to README.md
CONFIG_STR = ConfigEngine.get_docs()
