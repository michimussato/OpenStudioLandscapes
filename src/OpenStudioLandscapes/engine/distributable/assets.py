import pathlib
import zipfile
from pathlib import Path
from typing import Any, Generator

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *


@asset(
    **ASSET_HEADER_DISTRIBUTABLE,
    ins={
        "group_out": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)]),
        ),
    },
    deps=[
        AssetKey([*ASSET_HEADER_LANDSCAPE_MAP["key_prefix"], "landscape_map"]),
    ],
)
def distributable(
    context: AssetExecutionContext,
    group_out: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path] | AssetMaterialization | Any, None, None]:

    env = group_out.get("env", {})

    landscape_path = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
    )

    distributable_out = pathlib.Path(
        landscape_path,
        f"{env.get('LANDSCAPE', 'default')}_distributable.zip",
    )

    if distributable_out.exists():
        context.log.warning(
            f"Distributable file already exists: {distributable_out}. "
            "This file will only be created once. This is to avoid "
            "that i.e. prepared databases come with already pre-initialized content. "
            "Content might be outdated. "
            "Create a full new Landscape to create a new distributable."
        )
        raise FileExistsError(distributable_out)

    else:
        with zipfile.ZipFile(distributable_out, "w") as distributable_zip:
            for file_path in landscape_path.rglob("*"):
                if file_path == distributable_out:
                    # skip the actual Zip file to prevent
                    # recursion
                    continue

                context.log.info(f"Adding {file_path.as_posix()}")

                # Add file to zip
                distributable_zip.write(
                    filename=file_path,
                    arcname=file_path.relative_to(landscape_path),
                )

    yield Output(distributable_out)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(distributable_out),
        },
    )
