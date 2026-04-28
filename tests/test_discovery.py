import os
import pathlib
import shutil

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "AGPL-3.0"

__version__ = "0.1"
__maintainer__ = "Michael Mussato"
__email__ = "michimussato@gmail.com"


CLEANUP_ENABLED = True


fixtures = pathlib.Path(__file__).parent / "fixtures"
config_store: pathlib.Path = pathlib.Path(fixtures / "config-store")

os.environ["OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT"] = config_store.as_posix()

import pytest
import copy
from OpenStudioLandscapes.engine.config.models import (
    ConfigEngine,
    DockerConfigModel,
    DockerRegistryConfig,
    DockerRegistryAccess,
    DockerRegistryProtocol,
    DockerPullPolicy,
    RezConfigModel,
    SudoMethod,
)
from OpenStudioLandscapes.engine.discovery.discovery import (
    get_config_engine,
)


@pytest.fixture
def fixture_config_store():
    # Use fixtures:
    # - [Pytest - How to use fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html)
    # before test - create resource
    config_store.mkdir(parents=True, exist_ok=True)
    yield config_store
    # after test - remove resource
    if CLEANUP_ENABLED:
        shutil.rmtree(config_store)


def test_get_config_engine(
    fixture_config_store: pathlib.Path,
) -> None:

    # Careful, ConfigEngine is a Singleton
    expected = ConfigEngine(
        **{
            "openstudiolandscapes__docker_config": DockerConfigModel(
                **{
                    "use_registry": False,
                    "no_cache": False,
                    "docker_registry_config": DockerRegistryConfig(
                        **{
                            "docker_push": True,
                            "docker_pull": True,
                            "docker_repository_name": "openstudiolandscapes",
                            "docker_registry_access": DockerRegistryAccess.public,
                            "docker_registry_protocol": DockerRegistryProtocol.https,
                            "docker_registry_fqdn": "registry.openstudiolandscapes.lan",
                            "docker_registry_port": 5000,
                            "docker_registry_username": "registry-user",
                            "docker_registry_password": "registry-password",
                        },
                    ),
                    "docker_pull_policy": DockerPullPolicy.always,
                },
            ),
            "openstudiolandscapes__rez_config": RezConfigModel(
                **{
                    "rez_version": "3.3.0",
                    "REZ_LOCAL_PACKAGES_PATH": pathlib.Path("~/packages"),
                    "REZ_RELEASE_PACKAGES_PATH": pathlib.Path("~/.rez/packages/int"),
                    "REZ_EXTERNAL_PACKAGES_PATH": pathlib.Path("~/.rez/packages/ext"),
                    "apt_packages_rez": ["binutils"],
                }
            ),
            "apt_packages_base": [
                "git",
                "ca-certificates", "htop", "file", "tzdata", "curl", "wget", "ffmpeg", "libegl1", "libsm6",
                "libglu1-mesa", "libxss1", "sudo", "neovim", "xz-utils", "xvfb", "xauth",
            ],
            "apt_packages_build_python311": [
                "build-essential", "pkg-config", "zlib1g-dev", "libncurses5-dev",
                "libgdbm-dev", "libnss3-dev", "libssl-dev", "libreadline-dev", "libffi-dev",
                "libsqlite3-dev", "libbz2-dev", "iproute2", "liblzma-dev",
            ],
            "pip_packages": [],
            "openstudiolandscapes__domain_lan": "openstudiolandscapes.lan",
            "openstudiolandscapes__human_readable_ids": True,
            "sudo_method": SudoMethod.PKEXEC,
            "global_bind_volumes": [],
            "global_environment_variables": {},
            "tz": "Europe/UTC",
        },
    )

    result_singleton = get_config_engine()

    assert result_singleton is expected

    expected_dump = copy.deepcopy(expected.model_dump())
    del expected  # delete expected ConfigModel so that we can create a new Singleton -> move to fixture?
    del result_singleton

    result = get_config_engine()
    result_dump = result.model_dump()

    assert isinstance(result, ConfigEngine)
    assert result_dump == expected_dump
