import os
import pathlib

from pydantic import BaseModel, field_validator

from dagster import (
    get_dagster_logger,
)

LOG = get_dagster_logger(__name__)


"""
Resources:
- https://app.studyraid.com/en/read/15002/518529/conditional-validation-based-on-other-fields
"""


# Todo
#  - [ ] Learn about serialization
#        - https://docs.pydantic.dev/latest/concepts/serialization/


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
    docker_push: bool
    docker_pull: bool
    docker_repository_name: str
    docker_registry_access: str
    docker_registry_protocol: str
    docker_registry_fqdn: str
    docker_registry_port: int  # PositiveInt
    docker_registry_username: str
    docker_registry_password: str

    @field_validator("docker_repository_name")
    @classmethod
    def lowercase_docker_repository_name(cls, value):
        # Do not:
        # - repeat special characters multiple times (like "__")
        # - use capitals in repository names
        return value.lower()


class DockerConfigModel(BaseModel):

    use_registry: bool
    no_cache: bool
    docker_registry_config: DockerRegistryConfig

    # @field_validator("docker_registry_config")
    # @classmethod
    # def ensure_valid__docker_registry_config(
    #     cls,
    #     docker_registry_config: bool,
    #     values: ValidationInfo,
    # ):
    #
    #     # docker_registry_config = _DockerRegistryConfig(docker_repository_type=_DockerRepositoryType(repository_type=<DockerRepositoryType.PUBLIC: 'public'>, repository_name='some_name'), docker_registry_url='registry.helloworld.com', docker_registry_port=5000, docker_registry_username='registry-user', docker_registry_password='registry-password')
    #     # type(docker_registry_config) = <class 'OpenStudioLandscapes.engine.config.validate_config._DockerRegistryConfig'>
    #     # dir(docker_registry_config) = ['__abstractmethods__', '__annotations__', '__class__', '__class_getitem__', '__class_vars__', '__copy__', '__deepcopy__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__fields__', '__fields_set__', '__format__', '__ge__', '__get_pydantic_core_schema__', '__get_pydantic_json_schema__', '__getattr__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__pretty__', '__private_attributes__', '__pydantic_complete__', '__pydantic_computed_fields__', '__pydantic_core_schema__', '__pydantic_custom_init__', '__pydantic_decorators__', '__pydantic_extra__', '__pydantic_fields__', '__pydantic_fields_set__', '__pydantic_generic_metadata__', '__pydantic_init_subclass__', '__pydantic_on_complete__', '__pydantic_parent_namespace__', '__pydantic_post_init__', '__pydantic_private__', '__pydantic_root_model__', '__pydantic_serializer__', '__pydantic_setattr_handlers__', '__pydantic_validator__', '__reduce__', '__reduce_ex__', '__replace__', '__repr__', '__repr_args__', '__repr_name__', '__repr_recursion__', '__repr_str__', '__rich_repr__', '__setattr__', '__setstate__', '__signature__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__weakref__', '_abc_impl', '_calculate_keys', '_copy_and_set_values', '_get_value', '_iter', '_setattr_handler', 'construct', 'copy', 'dict', 'docker_registry_password', 'docker_registry_port', 'docker_registry_url', 'docker_registry_username', 'docker_repository_type', 'from_orm', 'json', 'model_computed_fields', 'model_config', 'model_construct', 'model_copy', 'model_dump', 'model_dump_json', 'model_extra', 'model_fields', 'model_fields_set', 'model_json_schema', 'model_parametrized_name', 'model_post_init', 'model_rebuild', 'model_validate', 'model_validate_json', 'model_validate_strings', 'parse_file', 'parse_obj', 'parse_raw', 'schema', 'schema_json', 'update_forward_refs', 'validate']
    #
    #     # values = ValidationInfo(config={'title': 'DockerRegistryConfigModel'}, context=None, data={'use_registry': True}, field_name='docker_registry_config')
    #     # dir(values) = ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'config', 'context', 'data', 'field_name', 'mode']
    #     if values.data.get("use_registry"):
    #         if docker_registry_config is None:
    #             raise ValueError("`use_registry` is enabled. "
    #                              "All fields must be set.")


class ConfigEngine(BaseModel):

    openstudiolandscapes__docker_config: DockerConfigModel

    openstudiolandscapes__repository_root: pathlib.Path = pathlib.Path(
        os.environ.get(
            "OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT",
            default="~/git/repos/OpenStudioLandscapes"
        )
    )

    openstudiolandscapes__configstore_root: pathlib.Path = pathlib.Path(
        os.environ.get(
            "OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT",
            default="~/.config/OpenStudioLandscapes/config-store",
        )
    )

    openstudiolandscapes__domain_lan: str = os.environ.get(
        "OPENSTUDIOLANDSCAPES__DOMAIN_LAN",
        default="openstudiolandscapes.lan",
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

    @field_validator("openstudiolandscapes__repository_root")
    @classmethod
    def ensure_valid__openstudiolandscapes__repository_root(cls, value: pathlib.Path):
        _value = value.expanduser().resolve()
        if not _value.exists():
            # Create directory
            _value.mkdir(parents=True, exist_ok=True)
        if not _value.is_dir():
            raise ValueError(
                "`openstudiolandscapes__repository_root` is not a valid directory."
            )
        return value

    @field_validator("openstudiolandscapes__configstore_root")
    @classmethod
    def ensure_valid__openstudiolandscapes__configstore_root(cls, value: pathlib.Path):
        _value = value.expanduser().resolve()
        if not _value.exists():
            # Create directory
            _value.mkdir(parents=True, exist_ok=True)
        if not _value.is_dir():
            raise ValueError(
                "`openstudiolandscapes__configstore_root` is not a valid directory."
            )
        return value

    # @field_validator("openstudiolandscapes__config_yml")
    # @classmethod
    # def ensure_valid__openstudiolandscapes__config_yml(cls, value: pathlib.Path):
    #     _value = value.expanduser().resolve()
    #     if not _value.parent.exists():
    #         # Create parent directories
    #         _value.parent.mkdir(parents=True, exist_ok=True)
    #     # if not _value.is_file():
    #     #     raise ValueError(
    #     #         "`openstudiolandscapes__config_yml` is not a valid file."
    #     #     )
    #     return _value

    # @field_validator("kitsu_db_password")
    # @classmethod
    # def ensure_valid__kitsu_db_password(cls, value: str):
    #     if value == "mysecretpassword":
    #         return value
    #     else:
    #         raise ValueError(
    #             "`kitsu_db_password` (as the initial default) "
    #             "must be `mysecretpassword` for now. Other "
    #             "values will render Kitsu inoperable"
    #         )
    #
    # @field_validator("kitsu_port_container")
    # @classmethod
    # def ensure_valid__kitsu_port_container(cls, value: int):
    #     if value == 80:
    #         return value
    #     else:
    #         raise ValueError(
    #             "`kitsu_port_container` must be set "
    #             "to 80 for now. Other values will render Kitsu inoperable."
    #         )
    #
    # # @field_validator("kitsu_postgres_conf")
    # # @classmethod
    # # def ensure_valid__kitsu_postgres_conf(cls, value: pathlib.PosixPath):
    # #     if value.exists():
    # #         return value
    # #     else:
    # #         raise ValueError(f"`kitsu_postgres_conf` ({value.as_posix()}) "
    # #                          f"does not exist.")
