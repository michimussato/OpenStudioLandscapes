import pathlib
from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field

from OpenStudioLandscapes.engine.config.models import ConfigEngine, FeatureBaseModel


class OpenStudioLandscapesBaseOut(BaseModel):
    # MAKE SINGLETON
    env: Dict[str, str]
    #   "env": {
    #     "GIT_ROOT": "/home/michael/git/repos/OpenStudioLandscapes",
    #     "DOT_LANDSCAPES": "/home/michael/git/repos/OpenStudioLandscapes/.landscapes",
    #     "DOT_SHARED_VOLUMES": ".shared_volumes",
    #     "DOT_FEATURES": "/home/michael/git/repos/OpenStudioLandscapes/.features",
    #     "DOT_OVERRIDES": "/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-12-14-19-18-32-49ccd914b2a94c3480c99baed42570af/.overrides",
    #     "AUTHOR": "michimussato@gmail.com",
    #     "CREATED_BY": "michael",
    #     "CREATED_ON": "lenovo",
    #     "CREATED_AT": "2025-12-14_19-18-40",
    #     "TIMEZONE": "Europe/Zurich",
    #     "DEFAULT_CONFIG_DBPATH": "/data/configdb",
    #     "PYTHON_MAJ": "3",
    #     "PYTHON_MIN": "11",
    #     "PYTHON_PAT": "11",
    #     "LANDSCAPE": "2025-12-14-19-18-32-49ccd914b2a94c3480c99baed42570af"
    #   },
    config_engine: ConfigEngine
    #   "config_engine": "openstudiolandscapes__docker_config=DockerConfigModel(use_registry=True, no_cache=False, docker_registry_config=DockerRegistryConfig(docker_push=True, docker_pull=True, docker_repository_name='openstudiolandscapes', docker_registry_access='public', docker_registry_protocol='https', docker_registry_fqdn='registry.openstudiolandscapes.lan', docker_registry_port=5000, docker_registry_username='registry-user', docker_registry_password='registry-password')) openstudiolandscapes__repository_root=PosixPath('{REPOSITORY_ROOT}') openstudiolandscapes__domain_lan='openstudiolandscapes.lan'",
    # This is part of ConfigEngine
    # docker_config: DockerConfigModel
    # #   "docker_config": {
    # #     "docker_push": true,
    # #     "docker_pull": true,
    # #     "docker_repository_name": "openstudiolandscapes",
    # #     "docker_registry_access": "public",
    # #     "docker_registry_protocol": "https",
    # #     "docker_registry_fqdn": "registry.openstudiolandscapes.lan",
    # #     "docker_registry_port": 5000,
    # #     "docker_registry_username": "registry-user",
    # #     "docker_registry_password": "registry-password",
    # #     "docker_repository": "openstudiolandscapes",
    # #     "docker_repository_type": "public",
    # #     "docker_registry_url": "registry.openstudiolandscapes.lan",
    # #     "docker_use_local": false
    # #   },
    docker_config_json: pathlib.Path
    #   "docker_config_json": "/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-12-14-19-18-32-49ccd914b2a94c3480c99baed42570af/OpenStudioLandscapes/OpenStudioLandscapes_Base__docker_config_json",

    # Todo
    #  - [ ] Create DockerImageModel
    docker_image_base: Dict[str, Any]
    #   "docker_image": {
    #     "image_name": "openstudiolandscapes_base_build_docker_image",
    #     "image_prefixes": "registry.openstudiolandscapes.lan:5000/openstudiolandscapes/",
    #     "image_tags": [
    #       "2025-12-14-19-18-32-49ccd914b2a94c3480c99baed42570af"
    #     ],
    #     "image_parent": {}
    #   }
    # config_engine: ConfigEngine


class OpenStudioLandscapesFeatureBasePort(BaseModel):
    compose: Union[None, Dict[str, Any]] = Field(
        default=None,
    )


class OpenStudioLandscapesFeatureIn(OpenStudioLandscapesFeatureBasePort):
    openstudiolandscapes_base: OpenStudioLandscapesBaseOut

    feature_in_parent: Union[None, "OpenStudioLandscapesFeatureOut"] = Field(
        default=None,
    )


class OpenStudioLandscapesFeatureOut(OpenStudioLandscapesFeatureBasePort):
    config_feature: FeatureBaseModel

    cmd_extend: Union[None, List] = Field(
        default=None,
    )

    cmd_append: Union[None, Dict] = Field(
        default=None,
    )
