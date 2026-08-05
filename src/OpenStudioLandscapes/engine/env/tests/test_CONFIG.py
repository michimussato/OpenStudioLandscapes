import os
import pathlib
import shutil

fixtures = pathlib.Path(__file__).parent / "fixtures"
config_store = pathlib.Path(fixtures / "config-store")

os.environ["OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT"] = config_store.as_posix()

from typing import Generator

import pytest
from dagster import AssetMaterialization, Output, build_asset_context

from OpenStudioLandscapes.engine.config.models import (
    ConfigEngine,
    DockerPullPolicy,
    DockerRegistryAccess,
    DockerRegistryProtocol,
    SudoMethod,
)
from OpenStudioLandscapes.engine.env.assets import CONFIG

CLEANUP_ENABLED = True


# Set environment variables
# - https://medium.com/@odidaodida/python-overwrite-environment-variable-for-testing-56b3ce7ce1f2
# - https://stackoverflow.com/questions/36141024/how-to-pass-environment-variables-to-pytest
# - https://docs.pytest.org/en/7.2.x/how-to/fixtures.html#autouse-fixtures-fixtures-you-don-t-have-to-request


@pytest.fixture
def fixture_config_store():
    # Use fixtures:
    # - [Pytest - How to use fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html)
    # before test - create resource
    yield config_store
    # after test - remove resource
    if CLEANUP_ENABLED:
        shutil.rmtree(config_store)


# @pytest.fixture(autouse=True)
# def set_env(
#     fixture_config_store: pathlib.Path,
# ):
#     os.environ["OPENSTUDIOLANDSCAPES__CONFIGSTORE_ROOT"] = fixture_config_store.as_posix()


def test_CONFIG(
    fixture_config_store: pathlib.Path,
) -> None:

    context = build_asset_context()

    asset_return_generator: Generator[
        Output[ConfigEngine] | AssetMaterialization,
        None,
        None,
    ] = CONFIG(
        context=context,
    )

    result = [i for i in asset_return_generator]

    output: Output = result[0]
    config_engine: ConfigEngine = output.value
    actual = config_engine.model_dump()
    asset_materialization: AssetMaterialization = result[1]

    expected = {
        "apt_packages_base": [
            "git",
            "ca-certificates",
            "htop",
            "file",
            "tzdata",
            "curl",
            "wget",
            "ffmpeg",
            "libegl1",
            "libsm6",
            "libglu1-mesa",
            "libxss1",
            "sudo",
            "neovim",
            "xz-utils",
            "xvfb",
            "xauth",
        ],
        "apt_packages_build_python311": [
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
        "global_bind_volumes": [],
        "global_environment_variables": {},
        "openstudiolandscapes__docker_config": {
            "docker_pull_policy": DockerPullPolicy.always,
            "docker_registry_config": {
                "docker_pull": True,
                "docker_push": True,
                "docker_registry_access": DockerRegistryAccess.public,
                "docker_registry_fqdn": "registry.openstudiolandscapes.lan",
                "docker_registry_password": "registry-password",
                "docker_registry_port": 5000,
                "docker_registry_protocol": DockerRegistryProtocol.https,
                "docker_registry_username": "registry-user",
                "docker_repository_name": "openstudiolandscapes",
            },
            "no_cache": False,
            "use_registry": False,
        },
        "openstudiolandscapes__domain_lan": "openstudiolandscapes.lan",
        "openstudiolandscapes__human_readable_ids": True,
        "pip_packages": [],
        "sudo_method": SudoMethod.PKEXEC,
        "tz": "Europe/UTC",
    }

    assert actual == expected
