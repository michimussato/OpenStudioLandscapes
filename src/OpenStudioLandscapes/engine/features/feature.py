import re

from pathlib import(
Path,
)

from typing import (
List,
ClassVar,
Dict,
)

from pydantic import (
BaseModel,
Field,
field_validator,
)


class FeatureBase(BaseModel):
    """
    Base class for the FeatureModel.

    All features inherit from this class.

    Concept is described here:
    - https://stackoverflow.com/a/50099920/2207196
    """
    subclasses: ClassVar[Dict] = {}

    def __init_subclass__(cls, **kwargs):
        """
        This method is called when a subclass is instantiated.
        The instance will then be added to the base class subclasses list.

        Args:
            **kwargs:
        """
        super().__init_subclass__(**kwargs)
        cls.subclasses[cls.__name__] = cls

    enabled: bool = Field(
        default=True,
        description="Whether the Feature is enabled or not.",
    )
    # registry: DockerRegistryProtocol = DockerRegistryProtocol.http
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
        description="The name of the Dagster Asset Group.",
        frozen=True,
    )
    key_prefixes: List[str] = Field(
        description="The keys prefixes to add to each Dagster Asset.",
        examples=[
            "['Kitsu', 'OSS']",
        ]
    )
    docker_compose: Path = Field(
        default="{DOT_LANDSCAPES}/{LANDSCAPE}/{FEATURE}/docker_compose/docker-compose.yml",
        description="The path to the `docker-compose.yml` file.",
    )
    # compose_scope: ComposeScope = Field(
    #     default="default",
    #     examples=["default", "license_server", "worker"],
    # )
    # dependencies: List[str] = Field(examples=["OpenStudioLandscapes-Kitsu"])
    definitions: str = Field(
        description="The path to the `definitions.py` file.",
        examples=[
            "OpenStudioLandscapes.Kitsu.definitions",
        ],
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

    def __repr__(self):
        return f"Feature({[f'{k}={v}' for k, v in self.__dict__.items()]})"

    def __str__(self):
        return f"{self.feature_name}"


if __name__ == "__main__":
    pass
