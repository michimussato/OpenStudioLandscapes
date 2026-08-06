import json
import os
import pathlib
import shutil

__author__ = "Michael Mussato"
__copyright__ = "Michael Mussato"
__license__ = "AGPL-3.0"

__version__ = "0.1"
__maintainer__ = "Michael Mussato"
__email__ = "michimussato@gmail.com"

from typing import Generator, Dict

CLEANUP_ENABLED = False


FIXTURES = pathlib.Path(__file__).parent / "fixtures"
config_store: pathlib.Path = pathlib.Path(FIXTURES / "config-store")

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
def fixtures_base() -> Generator[pathlib.Path, None, None]:
    # Use fixtures:
    # - [Pytest - How to use fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html)
    # before test - create resource
    FIXTURES.mkdir(parents=True, exist_ok=True)
    yield FIXTURES
    # after test - remove resource
    # if CLEANUP_ENABLED:
    #     shutil.rmtree(FIXTURES)


@pytest.fixture
def fixtures_config_engine_dict() -> Generator[Dict, None, None]:
    # Use fixtures:
    # - [Pytest - How to use fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html)
    # before test - create resource
    config_engine_dict = {
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
    }
    yield config_engine_dict


@pytest.fixture
def fixture_config_store(
    fixtures_base,
) -> Generator[pathlib.Path, None, None]:
    config_store: pathlib.Path = pathlib.Path(fixtures_base / "config-store")
    config_store.mkdir(parents=True, exist_ok=True)
    yield config_store
    # if CLEANUP_ENABLED:
    #     shutil.rmtree(FIXTURES)


# @pytest.fixture
# def fixture_config_store_test(
#     fixture_config_store,
# ) -> Generator[pathlib.Path, None, None]:
#     config_store_test: pathlib.Path = pathlib.Path(fixture_config_store / "test")
#     config_store_test.mkdir(parents=True, exist_ok=True)
#     yield config_store_test
#     # if CLEANUP_ENABLED:
#     #     shutil.rmtree(FIXTURES)


def test_get_config_engine(
    fixture_config_store: pathlib.Path,
    fixtures_config_engine_dict: Dict,
) -> None:

    # Careful, ConfigEngine is a Singleton
    expected = ConfigEngine(
        **fixtures_config_engine_dict,
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


@pytest.fixture
def fixture_get_config_base(
    fixtures_base,
) -> Generator[pathlib.Path, None, None]:
    get_config: pathlib.Path = pathlib.Path(fixtures_base / "get-config")
    get_config.mkdir(parents=True, exist_ok=True)
    yield get_config
    # if CLEANUP_ENABLED:
    #     shutil.rmtree(FIXTURES)


@pytest.fixture
def fixture_get_config_base_testout(
    fixture_get_config_base,
) -> Generator[pathlib.Path, None, None]:
    get_config_testout: pathlib.Path = pathlib.Path(fixture_get_config_base / "testout")
    get_config_testout.mkdir(parents=True, exist_ok=True)
    yield get_config_testout
    # if CLEANUP_ENABLED:
    #     shutil.rmtree(FIXTURES)


def test_get_config(
    fixture_get_config_base: pathlib.Path,
    fixture_get_config_base_testout: pathlib.Path,
    fixtures_config_engine_dict: Dict,
):
    import ruamel.yaml
    from collections import OrderedDict
    from OpenStudioLandscapes.engine.discovery.discovery import get_config

    result_1 = get_config(
        file_path_config_yaml=fixture_get_config_base.joinpath("non-existing-config.yml"),
    )

    expected_1: ruamel.yaml.CommentedMap = ruamel.yaml.CommentedMap(
        OrderedDict(),
    )

    assert result_1 == expected_1

    result_2 = json.loads(
        json.dumps(
            get_config(
                file_path_config_yaml=fixture_get_config_base.joinpath("OpenStudioLandscapes", "config.yml"),
            ),
            indent=2,
            default=str,
        ),
    )

    config_engine: ConfigEngine = ConfigEngine(
        **fixtures_config_engine_dict,
    )

    # edit the model created from fixtures_config_engine_dict
    # arbitrarily
    config_engine.apt_packages_base.extend(
        [
            "my_additional_package",
        ]
    )

    # model_dump_json model; otherwise, nested models will just
    # dump as strings (not structured anymore).
    expected_2 = json.loads(
        config_engine.model_dump_json(
            indent=2,
            fallback=str,
        ),
    )

    assert result_2 == expected_2

    result_3 = json.loads(
        json.dumps(
            get_config(
                file_path_config_yaml=fixture_get_config_base.joinpath("OpenStudioLandscapes-Grafana", "config.yml"),
            ),
            indent=2,
            default=str,
        ),
    )

    print(json.dumps(result_3, indent=2, default=str))


