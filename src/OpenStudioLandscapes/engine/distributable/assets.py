import pathlib
import textwrap
import zipfile
from pathlib import Path
from typing import Any, Dict, Generator

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
from OpenStudioLandscapes.engine.link.models import OpenStudioLandscapesBaseOut


def add_file(
    context,
    distributable_zip,
    file_name,
    arcname,
) -> None:
    try:
        # Add file to zip

        context.log.info(f"Adding file: {file_name.as_posix()}")

        distributable_zip.write(
            filename=file_name,
            arcname=arcname,
        )
    except PermissionError as e:
        context.log.error(e)
    except OSError as e:
        context.log.error(e)


@asset(
    **ASSET_HEADER_DISTRIBUTABLE,
    ins={
        "group_out_base": AssetIn(
            AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)]),
        ),
    },
    deps=[
        AssetKey([*ASSET_HEADER_LANDSCAPE_MAP["key_prefix"], "landscape_map"]),
    ],
)
def distributable(
    context: AssetExecutionContext,
    group_out_base: OpenStudioLandscapesBaseOut,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path] | AssetMaterialization | Any, None, None]:

    env: Dict = group_out_base.env

    base_landscapes = pathlib.Path(env["DOT_LANDSCAPES"])

    landscape_id = env.get("LANDSCAPE", "default")

    shared_volumes = env["DOT_SHARED_VOLUMES"]

    landscape_path = base_landscapes / landscape_id

    tar_out = landscape_path / "dist"
    tar_out.mkdir(parents=True, exist_ok=True)

    distributable_out = pathlib.Path(
        tar_out,
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

            # Todo
            #  - [ ] This whole logic seems a bit clunky. Could be done better for sure

            # Process all the .files and .directories
            for file_path in base_landscapes.glob(".*"):

                for file_path_glob in file_path.rglob("*"):

                    context.log.debug(f"{file_path_glob = }")

                    # Skip if...
                    if file_path_glob.name == ".gitkeep":
                        context.log.info(f"File skipped: {file_path_glob.as_posix()}")
                        continue

                    if file_path_glob.name == ".gitignore":
                        context.log.info(f"File skipped: {file_path_glob.as_posix()}")
                        continue

                    if (
                        base_landscapes.joinpath(".acme.sh").as_posix()
                        in file_path_glob.as_posix()
                    ):
                        if not base_landscapes.joinpath(".acme.sh") == file_path_glob:
                            if not file_path_glob.match("*_ecc/*"):
                                context.log.warning(
                                    f"File skipped: {file_path_glob.as_posix()}"
                                )
                                continue

                    if (
                        base_landscapes.joinpath(".dagster", "postgres").as_posix()
                        in file_path_glob.as_posix()
                    ):
                        if (
                            not base_landscapes.joinpath(".dagster", "postgres")
                            == file_path_glob
                        ):
                            context.log.warning(
                                f"File skipped: {file_path_glob.as_posix()}"
                            )
                            continue

                    if (
                        base_landscapes.joinpath(".n8n").as_posix()
                        in file_path_glob.as_posix()
                    ):
                        if not base_landscapes.joinpath(".n8n") == file_path_glob:
                            context.log.warning(
                                f"File skipped: {file_path_glob.as_posix()}"
                            )
                            continue

                    if (
                        base_landscapes.joinpath(shared_volumes).as_posix()
                        in file_path_glob.as_posix()
                    ):
                        if (
                            len(
                                file_path_glob.relative_to(
                                    base_landscapes.joinpath(shared_volumes)
                                ).parts
                            )
                            > 1
                        ):
                            # Just add the base dir of the shared volumes but not its contents
                            context.log.warning(
                                f"File skipped: {file_path_glob.as_posix()}"
                            )
                            continue

                    if (
                        base_landscapes.joinpath(".n8n").as_posix()
                        in file_path_glob.as_posix()
                    ):
                        if not base_landscapes == file_path_glob.parent:
                            context.log.warning(
                                f"File skipped: {file_path_glob.as_posix()}"
                            )
                            continue

                    # context.log.warning(f"Adding file: {file_path_glob.as_posix()}")

                    add_file(
                        context=context,
                        distributable_zip=distributable_zip,
                        file_name=file_path_glob,
                        arcname=file_path_glob.relative_to(base_landscapes),
                    )

            # Proecess the Landscape and ignore all other
            # Landscapes that live inside the `base_landscape` directory
            for file_path in base_landscapes.joinpath(landscape_id).rglob("*"):

                context.log.debug(f"{base_landscapes = }")
                context.log.debug(f"{file_path = }")

                parts = file_path.relative_to(base_landscapes).parts
                context.log.debug(f"{parts = }")

                # skip the actual Zip file to prevent
                # recursion
                if file_path.name == distributable_out.name:
                    context.log.info(f"File skipped: {file_path.as_posix()}")
                    continue

                add_file(
                    context=context,
                    distributable_zip=distributable_zip,
                    file_name=file_path,
                    arcname=file_path.relative_to(base_landscapes),
                )

        with open(tar_out / "extract.sh", "w") as extract_sh:
            extract_sh.write(
                textwrap.dedent(
                    """\
                    #!/usr/bin/env bash
                    
                    SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

                    unzip -d "${SCRIPT_DIR}" %s
                    """
                )
                % distributable_out.name
            )

    yield Output(distributable_out)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(distributable_out),
        },
    )
