import getpass
import pathlib
import socket
import tempfile
import uuid
from datetime import datetime
from typing import Generator, MutableMapping

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
    multi_asset,
    AssetOut,
)

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *


@asset(
    **ASSET_HEADER_BASE_ENV,
)
def git_root(
    context: AssetExecutionContext,
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    _git_root = get_git_root()

    yield Output(_git_root)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_git_root),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
)
def landscape_id(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping[str, str]] | AssetMaterialization, None, None]:

    now = datetime.now()

    landscape_stamp = {
        "LANDSCAPE": f"{datetime.strftime(now, '%Y-%m-%d_%H-%M-%S')}__{uuid.uuid4().hex}".replace("__", "_").replace("_", "-"),
    }

    yield Output(landscape_stamp)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(landscape_stamp),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
    # ins={
    #     "git_root": AssetIn(
    #         AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "git_root"]),
    #     ),
    # },
)
def dot_landscapes(
    context: AssetExecutionContext,
    # git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    _dot_landscapes = pathlib.Path("/opt/openstudiolandscapes/.landscapes")
    # _dot_landscapes = git_root / ".landscapes"

    if not _dot_landscapes.expanduser().exists():
        try:
            _dot_landscapes.mkdir(
                mode=0o775,
                parents=True,
                exist_ok=True,
            )
        except PermissionError as e:
            context.log.exception("No permission to create .landscapes directory.")
            raise PermissionError(
                "No permission to create .landscapes directory. "
                f"Try `sudo mkdir -p {_dot_landscapes.as_posix()} "
                f"&& sudo chmod -R a+rw {_dot_landscapes.as_posix()}`."
            ) from e

        # raise FileNotFoundError(f"DOT_LANDSCAPES directory does not exist: "
        #                         f"{_dot_landscapes.as_posix()}. "
        #                         f"Try `sudo mkdir -p {_dot_landscapes.as_posix()} "
        #                         f"&& sudo chmod -R a+rw {_dot_landscapes.as_posix()}`.")

    if not _dot_landscapes.is_dir():
        raise NotADirectoryError(f"DOT_LANDSCAPES is not a directory: {_dot_landscapes.as_posix()}")

    # Test
    try:
        with tempfile.TemporaryFile(
            dir=_dot_landscapes,
            prefix="DOT_LANDSCAPES_WRITE_TEST",
            delete=True,
        ) as temp_file:
            temp_file.write("I was here.")
    except PermissionError as e:
        raise PermissionError(
            f"DOT_LANDSCAPES_WRITE_TEST permission error: "
            f"{_dot_landscapes.as_posix()} is not writable. "
            f"Try `sudo chmod -R a+rw {_dot_landscapes.as_posix()}`."
        ) from e

    # try:
    #     _dot_landscapes.mkdir(
    #         parents=True,
    #         exist_ok=True,
    #     )
    # except PermissionError as e:
    #     context.log.exception("Could not create Landscapes directory: %s", e)
    #     raise PermissionError(
    #         f"Could not create {_dot_landscapes.as_posix()}. "
    #         f"Try `sudo mkdir -p {_dot_landscapes.as_posix()} "
    #         f"&& sudo chown -R 7002:docker {_dot_landscapes.parent.as_posix()}`."
    #         # f"&& sudo chmod -R a+rw {_dot_landscapes.parent.as_posix()}`."
    #     ) from e

    yield Output(_dot_landscapes)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_dot_landscapes),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
    ins={
        "git_root": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "git_root"]),
        ),
    },
)
def dot_features(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    _dot_features = git_root / ".features"
    _dot_features.mkdir(
        parents=True,
        exist_ok=True,
    )

    yield Output(_dot_features)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_dot_features),
        },
    )


@multi_asset(
    outs={
        "env": AssetOut(
            **ASSET_HEADER_BASE_ENV,
            dagster_type=dict,
            description="",
        ),
        "features": AssetOut(
            **ASSET_HEADER_BASE_ENV,
            dagster_type=dict,
            description="",
        ),
    },
    ins={
        "git_root": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "git_root"])),
        "landscape_id": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "landscape_id"])),
        "dot_landscapes": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "dot_landscapes"])),
        "dot_features": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "dot_features"])),
        "nfs": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "nfs"])),
        "FEATURES": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "FEATURES"])),
    },
)
def env(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
    landscape_id: dict,  # pylint: disable=redefined-outer-name
    dot_landscapes: pathlib.Path,  # pylint: disable=redefined-outer-name
    dot_features: pathlib.Path,  # pylint: disable=redefined-outer-name
    nfs: dict,  # pylint: disable=redefined-outer-name
    FEATURES: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    # @formatter:off
    # Todo
    #  - [ ] Move to constants.py
    ENVIRONMENT_BASE: dict = {
        "GIT_ROOT": git_root.as_posix(),
        # Todo
        #  - [ ] Move CONFIGS_ROOT to individual modules
        "CONFIGS_ROOT": pathlib.Path(
            git_root,
            "configs",
        ).as_posix(),
        "DOT_LANDSCAPES": dot_landscapes.as_posix(),
        "DOT_FEATURES": dot_features.as_posix(),
        "AUTHOR": "michimussato@gmail.com",
        "CREATED_BY": str(getpass.getuser()),
        "CREATED_ON": str(socket.gethostname()),
        "CREATED_AT": str(datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")),
        "TIMEZONE": "Europe/Zurich",
        # "IMAGE_PREFIX": "michimussato",
        # Todo:
        #  - [ ] Where is this being used?
        "DEFAULT_CONFIG_DBPATH": "/data/configdb",
        "ROOT_DOMAIN": "farm.evil",
        # https://vfxplatform.com/
        "PYTHON_MAJ": "3",
        "PYTHON_MIN": "11",
        "PYTHON_PAT": "11",
    }

    ENVIRONMENT_BASE.update(landscape_id)
    ENVIRONMENT_BASE.update(nfs)
    # @formatter:on

    yield Output(
        output_name="env",
        value=ENVIRONMENT_BASE,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("env"),
        metadata={
            "__".join(context.asset_key_for_output("env").path): MetadataValue.json(ENVIRONMENT_BASE),
        },
    )

    yield Output(
        output_name="features",
        value=FEATURES,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("features"),
        metadata={
            "__".join(context.asset_key_for_output("features").path): MetadataValue.json(FEATURES),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
)
def nfs(
    context: AssetExecutionContext,
) -> Generator[Output[MutableMapping] | AssetMaterialization, None, None]:
    # @formatter:off
    _env: dict = {
        "NFS_ENTRY_POINT": pathlib.Path("/data/share/nfs").as_posix(),
        "NFS_ENTRY_POINT_LNS": pathlib.Path("/nfs").as_posix(),
        "INSTALLERS_ROOT": pathlib.Path("/data/share/nfs/installers").as_posix(),
    }
    # @formatter:on

    yield Output(_env)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_env),
        },
    )
