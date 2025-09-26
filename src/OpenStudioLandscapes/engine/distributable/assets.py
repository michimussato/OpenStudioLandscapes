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

    base_landscapes = pathlib.Path(env.get("DOT_LANDSCAPES"))

    landscape_id = env.get("LANDSCAPE", "default")

    landscape_path = base_landscapes / landscape_id

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
            context.log.info(f"Creating Distributable...")
            context.log.info(f"{base_landscapes.as_posix() = }")
            context.log.info(f"{landscape_id = }")
            # Todo:
            #  - [ ] contolling what ends up in the Zip file
            #        and what does not could be more dynamic
            for file_path in base_landscapes.rglob("*"):

                # skip the actual Zip file to prevent
                # recursion
                if file_path.name == distributable_out.name:
                    context.log.info(f"File skipped: {file_path.as_posix()}")
                    continue

                # Skip if...
                if file_path.name == ".gitkeep":
                    context.log.info(f"File skipped: {file_path.as_posix()}")
                    continue

                if file_path.name == ".gitignore":
                    context.log.info(f"File skipped: {file_path.as_posix()}")
                    continue

                if (
                    base_landscapes.joinpath(".acme.sh").as_posix()
                    in file_path.as_posix()
                ):
                    if not base_landscapes.joinpath(".acme.sh") == file_path:
                        if not file_path.match("*_ecc/*"):
                            context.log.warning(f"File skipped: {file_path.as_posix()}")
                            continue

                if (
                    base_landscapes.joinpath(".dagster", "postgres").as_posix()
                    in file_path.as_posix()
                ):
                    if (
                        not base_landscapes.joinpath(".dagster", "postgres")
                        == file_path
                    ):
                        context.log.warning(f"File skipped: {file_path.as_posix()}")
                        continue

                if base_landscapes.joinpath(".n8n").as_posix() in file_path.as_posix():
                    if not base_landscapes.joinpath(".n8n") == file_path:
                        context.log.warning(f"File skipped: {file_path.as_posix()}")
                        continue

                if (
                    base_landscapes.joinpath(".shared_volumes").as_posix()
                    in file_path.as_posix()
                ):
                    if (
                        len(
                            file_path.relative_to(
                                base_landscapes.joinpath(".shared_volumes")
                            ).parts
                        )
                        > 1
                    ):
                        # Just add the base dir of the shared volumes but not its contents
                        context.log.warning(f"File skipped: {file_path.as_posix()}")
                        continue

                if base_landscapes.joinpath(".n8n").as_posix() in file_path.as_posix():
                    if not base_landscapes == file_path.parent:
                        context.log.warning(f"File skipped: {file_path.as_posix()}")
                        continue

                context.log.info(f"Adding {file_path.as_posix()}")

                try:
                    # Add file to zip
                    distributable_zip.write(
                        filename=file_path,
                        arcname=file_path.relative_to(base_landscapes),
                    )
                except PermissionError as e:
                    context.log.error(e)
                except OSError as e:
                    context.log.error(e)

    yield Output(distributable_out)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(distributable_out),
        },
    )
