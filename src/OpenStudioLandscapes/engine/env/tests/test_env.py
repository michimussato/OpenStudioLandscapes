import pathlib
import shutil
from typing import Dict

import pytest
# https://docs.dagster.io/guides/test/unit-testing-assets-and-ops#unit-test-examples


from dagster import (
    IOManager,
    Definitions,
    SourceAsset,
)


CLEANUP_ENABLED = True


fixtures = pathlib.Path(__file__).parent / "fixtures"


# Unit Testing ops and assets
# - https://docs.dagster.io/guides/test/unit-testing-assets-and-ops
# Testing with `context`
# - https://docs.dagster.io/guides/test/unit-testing-assets-and-ops#context
# Testing `multi_asset`
# - https://release-1-9-13.archive.dagster-docs.io/guides/test/unit-testing-assets-and-ops#multi-assets-upstream
# - https://github.com/dagster-io/dagster/issues/16195

# from dagster import Definitions, SourceAsset, AssetKey
# from OpenStudioLandscapes.engine.constants import ASSET_HEADER_BASE_ENV
from OpenStudioLandscapes.engine.env.assets import (
    env,
    git_root,
    dot_landscapes,
    landscape_id,
    dot_features,
)


class MockDataIOManager(IOManager):
    def __init__(
            self,
            dot_landscapes: pathlib.Path,
            git_root: pathlib.Path,
            landscape_id: Dict[str, str],
            dot_features: pathlib.Path,
    ):
        self.dot_landscapes = dot_landscapes
        self.git_root = git_root
        self.landscape_id = landscape_id
        self.dot_features = dot_features

    def load_input(self, context):
        asset_key_path = context.asset_key.path
        if asset_key_path == dot_landscapes.key.path:
            return self.dot_landscapes
        elif asset_key_path == git_root.key.path:
            return self.git_root
        elif asset_key_path == landscape_id.key.path:
            return self.landscape_id
        elif asset_key_path == dot_features.key.path:
            return self.dot_features
        else:
            raise ValueError(f"Unexpected asset key: {asset_key_path}")

    def handle_output(self, context, obj):
        pass


@pytest.fixture
def fixture_dot_landscapes():
    # Use fixtures:
    # - [Pytest - How to use fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html)
    # before test - create resource
    fixture_dot_landscapes_ = fixtures / "dot_landscapes"
    yield fixture_dot_landscapes_
    # after test - remove resource
    if CLEANUP_ENABLED:
        shutil.rmtree(fixture_dot_landscapes_)


def test_env(
        fixture_dot_landscapes: pathlib.Path,
) -> None:

    source_dot_landscapes = SourceAsset(key=dot_landscapes.key)
    source_git_root = SourceAsset(key=git_root.key)
    source_landscape_id = SourceAsset(key=landscape_id.key)
    source_dot_features = SourceAsset(key=dot_features.key)

    defs = Definitions(
        assets=[
            source_dot_landscapes,
            source_git_root,
            source_landscape_id,
            source_dot_features,
            env,
        ],
        resources={
            "io_manager": MockDataIOManager(
                dot_landscapes=fixture_dot_landscapes,
                git_root=pathlib.Path(fixtures / "git_root"),
                landscape_id={
                    "LANDSCAPE": "2026-04-11_23-04-39__sheer-inky-dynamic-song",
                },
                dot_features=pathlib.Path(fixtures / "dot_features"),
            )
        },
    )

    job = defs.get_implicit_global_asset_job_def()
    result = job.execute_in_process(
        asset_selection=[
            env.key,
        ]
    )

    assert result.success
