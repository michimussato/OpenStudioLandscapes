import datetime
import getpass
import json
import os
import pathlib
import socket
import tempfile
import textwrap
import uuid
from typing import Generator, MutableMapping

import pytz
import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    AssetOut,
    MetadataValue,
    Output,
    asset,
    multi_asset,
)
from human_readable_id import generate_hrid

import OpenStudioLandscapes.engine.discovery.discovery as discovery
from OpenStudioLandscapes.engine import exceptions
from OpenStudioLandscapes.engine.config.models import CONFIG_STR, ConfigEngine
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *


# Todo
#  - [ ] Move this to ConfigEngine?
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


# Todo
#  - [ ] Move this to ConfigEngine?
@asset(
    **ASSET_HEADER_BASE_ENV,
    ins={
        "CONFIG": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "CONFIG"])),
    },
)
def landscape_id(
    context: AssetExecutionContext,
    CONFIG: ConfigEngine,  # pylint: disable=redefined-outer-name
) -> Generator[Output[MutableMapping[str, str]] | AssetMaterialization, None, None]:

    landscape_id = os.environ.get("OPENSTUDIOLANDSCAPES__LANDSCAPE_ID", None)

    if landscape_id is None:

        now = datetime.datetime.now()

        now_prefix = datetime.datetime.strftime(now, "%Y-%m-%d_%H-%M-%S")

        if CONFIG.openstudiolandscapes__human_readable_ids:
            id_ = generate_hrid(
                words=4,
                separator="-",
                numbers=0,
            )

        else:
            id_ = uuid.uuid4().hex

        landscape_id = "__".join(
            [
                now_prefix,
                id_,
            ]
        )

    landscape_stamp = {
        "LANDSCAPE": landscape_id,
    }

    yield Output(landscape_stamp)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "LANDSCAPE": MetadataValue.path(landscape_stamp["LANDSCAPE"]),
        },
    )


# Todo
#  - [ ] Move this to ConfigEngine?
@asset(
    **ASSET_HEADER_BASE_ENV,
    ins={
        "git_root": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "git_root"]),
        ),
    },
)
def dot_landscapes(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

    _dot_landscapes = pathlib.Path(
        get_str_env(
            env="OPENSTUDIOLANDSCAPES__DOT_LANDSCAPES_ROOT",
            default=git_root.as_posix(),
        ),
        ".landscapes",
    )

    if not _dot_landscapes.expanduser().exists():
        try:
            _dot_landscapes.mkdir(
                mode=0o775,
                parents=True,
                exist_ok=True,
            )

            context.log.debug(f"{_dot_landscapes.as_posix()} was created successfully.")

        except PermissionError as e:
            context.log.exception("No permission to create .landscapes directory.")
            raise PermissionError(
                "No permission to create .landscapes root directory. \n"
                f"Try `"
                f"sudo install "
                f"--directory "
                f"--mode=0755 "
                f"--owner=$USER "
                f"--group=$(id --group --name $USER) "
                f"{_dot_landscapes.parent.as_posix()}"
                f"`."
            ) from e

    if not _dot_landscapes.is_dir():
        raise NotADirectoryError(
            f"DOT_LANDSCAPES is not a directory: {_dot_landscapes.as_posix()}"
        )

    # Write Test
    try:
        with tempfile.NamedTemporaryFile(
            dir=_dot_landscapes,
            prefix=".DOT_LANDSCAPES_WRITE_TEST__",
            delete=True,
            mode="w",
            encoding="utf-8",
        ) as temp_file:
            temp_file.writelines(
                [
                    "I was here.",
                ]
            )

        context.log.debug(
            f"Write test to {_dot_landscapes.as_posix()} completed successfully."
        )

    except PermissionError as e:
        raise PermissionError(
            f"DOT_LANDSCAPES_WRITE_TEST permission error: "
            f"{_dot_landscapes.as_posix()} is not writable. "
            f"Try `sudo chmod -R a+rw {_dot_landscapes.as_posix()}`."
        ) from e

    yield Output(_dot_landscapes)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_dot_landscapes),
        },
    )


# Todo
#  - [ ] Move this to ConfigEngine?
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

    context.log.debug(f"{_dot_features.as_posix()} created successfully.")

    yield Output(_dot_features)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(_dot_features),
        },
    )


@asset(
    **ASSET_HEADER_BASE_ENV,
    ins={},
    description=textwrap.dedent(f"""
Reads options from a custom `config.yml`.
If the custom `config.yml` does not exist, it 
will be created locally containing default options.

---

For reference, the default `config.yml` looks as follows:
        
```yaml
{CONFIG_STR}
```
"""),
)
def CONFIG(
    context: AssetExecutionContext,
    # env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[ConfigEngine] | AssetMaterialization,
    None,
    None,
]:

    config_validated = discovery.get_config_engine()

    yield Output(config_validated)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.md(
                f"```yaml\n{yaml.safe_dump(json.loads(config_validated.model_dump_json(fallback=str, indent=2)))}\n```"
            ),
        },
    )


@multi_asset(
    outs={
        "env": AssetOut(
            **ASSET_HEADER_BASE_ENV,
            dagster_type=dict,
            description="",
        ),
    },
    ins={
        "git_root": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "git_root"])
        ),
        "landscape_id": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "landscape_id"])
        ),
        "dot_landscapes": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "dot_landscapes"])
        ),
        "dot_features": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "dot_features"])
        ),
    },
)
def env(
    context: AssetExecutionContext,
    git_root: pathlib.Path,  # pylint: disable=redefined-outer-name
    landscape_id: dict,  # pylint: disable=redefined-outer-name
    dot_landscapes: pathlib.Path,  # pylint: disable=redefined-outer-name
    dot_features: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    # @formatter:off
    # # Todo
    # #  - [ ] Move to constants.py
    # tz = get_str_env(
    #     env="CONTAINER_TIMEZONE",
    #     default="Europe/Zurich",
    # )

    # if tz not in pytz.all_timezones:
    #     raise Exception(f"Unknown container timezone: {tz}")

    landscape_root_dir = pathlib.Path(dot_landscapes, landscape_id["LANDSCAPE"])

    try:
        landscape_root_dir.expanduser().mkdir(
            exist_ok=True,
            parents=True,
        )

        context.log.debug(f"{landscape_root_dir.as_posix()} created successfully.")

    except Exception as e:
        raise exceptions.OpenStudioLandscapesException(
            f"OpenStudioLandscapes could not create landscape root directory: {landscape_root_dir.as_posix()}."
        ) from e

    ENVIRONMENT_BASE: dict = {
        "GIT_ROOT": git_root.as_posix(),
        "DOT_LANDSCAPES": dot_landscapes.as_posix(),
        # Todo
        #  - [ ] move DOT_SHARED_VOLUMES to config.yml
        "DOT_SHARED_VOLUMES": ".shared_volumes",
        "DOT_FEATURES": dot_features.as_posix(),
        "DOT_OVERRIDES": pathlib.Path(landscape_root_dir, ".overrides").as_posix(),
        "AUTHOR": "michimussato@gmail.com",
        "CREATED_BY": str(getpass.getuser()),
        "CREATED_ON": str(socket.gethostname()),
        "CREATED_AT": str(
            datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H-%M-%S")
        ),
        # Todo
        #  - [ ] move TIMEZONE to config.yml
        # "TIMEZONE": str(tz),
        "PYTHON_MAJ": "3",
        "PYTHON_MIN": "11",
        "PYTHON_PAT": "11",
    }

    ENVIRONMENT_BASE.update(landscape_id)
    # @formatter:on

    yield Output(
        output_name="env",
        value=ENVIRONMENT_BASE,
    )

    yield AssetMaterialization(
        asset_key=context.asset_key_for_output("env"),
        metadata={
            "__".join(context.asset_key_for_output("env").path): MetadataValue.json(
                ENVIRONMENT_BASE
            ),
        },
    )
