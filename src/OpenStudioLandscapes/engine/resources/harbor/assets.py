import configparser
import os
import pathlib
import shutil
import textwrap
from pathlib import Path
from typing import Generator, List, Any

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
from OpenStudioLandscapes.engine.resources.harbor.constants import *
from OpenStudioLandscapes.engine.exceptions import OpenStudioLandscapesException

from OpenStudioLandscapes.engine.resources.harbor.resources import HarborResource


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    description=textwrap.dedent(
        f"""
        Harbor URL: {os.environ['OPENSTUDIOLANDSCAPES__HARBOR_URL']}
        
        Dev Center: {os.environ['OPENSTUDIOLANDSCAPES__HARBOR_URL']}/devcenter-api-2.0
        """.format(
            **os.environ
        ).format(
            **os.environ
        )
    )
)
def harbor_popen(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
) -> Generator[Output[int] | AssetMaterialization, None, None]:

    # cmd_harbor_up = harbor_resource.harbor_up(detached=True)

    harbor_up = harbor_resource.harbor_up()

    if harbor_up:
        raise OpenStudioLandscapesException("Could not start Harbor")
    # else:
    #     ret = harbor_resource.proc

    library_exists = harbor_resource.query_project_exists(
        project_name="library",
    )

    context.log.info(f"Library exists: {library_exists}")

    project_exists = harbor_resource.query_project_exists(
        project_name="openstudiolandscapes",
    )

    context.log.info(f"Project exists: {project_exists}")

    random_exists = harbor_resource.query_project_exists(
        project_name="random",
    )

    context.log.info(f"Random exists: {random_exists}")

    yield Output(harbor_up)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            # "cmd_harbor_up": MetadataValue.path(" ".join(harbor_resource.cmd_harbor_up)),
            "cmd_harbor_up_detached": MetadataValue.path(" ".join(harbor_resource.cmd_harbor_up_detached)),
            "cmd_harbor_down": MetadataValue.path(" ".join(harbor_resource.cmd_harbor_down)),
            "cmd_harbor_restart": MetadataValue.path(" ".join(harbor_resource.cmd_harbor_restart)),
            "cmd_harbor_ps": MetadataValue.path(" ".join(harbor_resource.cmd_harbor_ps)),
            "systeminfo": MetadataValue.json(harbor_resource.systeminfo().json()),
            "systeminfo_volumes": MetadataValue.json(harbor_resource.systeminfo_volumes().json()),
            "projects": MetadataValue.json(harbor_resource.list_projects().json()),
            "library_exists": MetadataValue.text(f"{library_exists.status_code = }"),
            "project_exists": MetadataValue.text(f"{project_exists.status_code = }"),
            "random_exists": MetadataValue.text(f"{random_exists.status_code = }"),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
    },
    deps=[
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "harbor_prepare"]),
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "harbor_popen"]),
    ],
    description=textwrap.dedent(
        f"""
        Harbor URL: {os.environ['OPENSTUDIOLANDSCAPES__HARBOR_URL']}
        
        Dev Center: {os.environ['OPENSTUDIOLANDSCAPES__HARBOR_URL']}/devcenter-api-2.0
        """.format(
            **os.environ
        ).format(
            **os.environ
        )
    )
)
def harbor_systemd(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
        env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path] | AssetMaterialization | Any, None, None]:

    unit_dict: dict = harbor_resource.systemd_unit_dict(context=context)

    unit: configparser.ConfigParser = configparser.ConfigParser()
    # Change from case insensitive to case sensitive
    # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.optionxform
    unit.optionxform = str

    unit.read_dict(unit_dict)

    unit_destination = pathlib.Path("/usr/lib/systemd/system")

    unit_file = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        f"{ASSET_HEADER_BASE['group_name']}__{'__'.join(ASSET_HEADER_BASE['key_prefix'])}",
        "__".join(context.asset_key.path),
        "systemd",
        "harbor.service",
    )

    unit_file.parent.mkdir(parents=True, exist_ok=True)

    with open(unit_file, "w") as fw:
        unit.write(fw, space_around_delimiters=False)

    with open(unit_file, "r") as fr:
        unit_file_content = fr.read()

    # ENABLE UNIT

    copy_service = [
        shutil.which("cp"),
        unit_file.as_posix(),
        unit_destination.as_posix(),
    ]

    set_permissions = [
        shutil.which("chmod"),
        "644",
        pathlib.Path(unit_destination, unit_file.name).as_posix(),
    ]

    daemon_reload = [
        shutil.which("systemctl"),
        "daemon-reload",
    ]

    systemctl_start = [
        shutil.which("systemctl"),
        "start",
        unit_file.name,
    ]

    systemctl_enable = [
        shutil.which("systemctl"),
        "enable",
        unit_file.name,
    ]

    install_service = [
        # shutil.which("pkexec"),
        *copy_service,
        "&&",
        *set_permissions,
        "&&",
        *daemon_reload,
        "&&",
        *systemctl_start,
        "&&",
        *systemctl_enable,
    ]

    # DISABLE UNIT

    systemctl_disable = [
        shutil.which("systemctl"),
        "disable",
        unit_file.name,
    ]

    systemctl_stop = [
        shutil.which("systemctl"),
        "stop",
        unit_file.name,
    ]

    remove_service = [
        shutil.which("rm"),
        pathlib.Path(unit_destination, unit_file.name).as_posix(),
    ]

    remove_service = [
        # shutil.which("pkexec"),
        *systemctl_disable,
        "&&",
        *systemctl_stop,
        "&&",
        *remove_service,
        "&&",
        *daemon_reload,
    ]

    # JOURNALCTL

    journalctl = [
        shutil.which("journalctl"),
        "--follow",
        f"--unit={unit_file.name}",
    ]

    su_method = {
        "su": [
            shutil.which("su"),
            "-",
            "root",
        ],
        "sudo": [
            shutil.which("sudo"),
            "--user=root",
        ],
        "pkexec": [
            shutil.which("pkexec"),
        ],
    }["pkexec"]

    sudo_bash_c = [
        *su_method,
        shutil.which("bash"),
        "-c",
    ]

    yield Output(unit_file)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(unit_file),
            "unit_dict": MetadataValue.json(unit_dict),
            unit_file.name: MetadataValue.md(f"```shell\n{unit_file_content}\n```"),
            # "journald": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(journalctl)}\""),
            "journald": MetadataValue.path(f"{' '.join(journalctl)}"),
            "install_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(install_service)}\""),
            "remove_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(remove_service)}\""),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
    },
    description=textwrap.dedent(
        f"""
        Harbor URL: {os.environ['OPENSTUDIOLANDSCAPES__HARBOR_URL']}
        
        Dev Center: {os.environ['OPENSTUDIOLANDSCAPES__HARBOR_URL']}/devcenter-api-2.0
        """.format(
            **os.environ
        ).format(
            **os.environ
        )
    )
)
def harbor_prepare(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
        env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path] | AssetMaterialization | Any, None, None]:

    harbor_root_dir: pathlib.Path = pathlib.Path(
        f"{os.environ['OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR']}".format(
            **os.environ,
            **env,
        )
    )

    git_clean = [
        shutil.which("git"),
        "clean",
        "-x",
        "--force",
        harbor_root_dir.as_posix(),
    ]

    su_method = {
        "su": [
            shutil.which("su"),
            "-",
            "root",
        ],
        "sudo": [
            shutil.which("sudo"),
            "--user=root",
        ],
        "pkexec": [
            shutil.which("pkexec"),
        ],
    }["pkexec"]

    sudo_bash_c = [
        *su_method,
        shutil.which("bash"),
        "-c",
    ]

    prepare: List = harbor_resource.harbor_prepare(context=context)

    yield Output(prepare)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            # "__".join(context.asset_key.path): MetadataValue.path(unit_file),
            # "unit_dict": MetadataValue.json(unit_dict),
            # unit_file.name: MetadataValue.md(f"```shell\n{unit_file_content}\n```"),
            "prepare": MetadataValue.path(f"{' '.join(prepare)}"),
            "git_clean": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(git_clean)}\""),
            # "install_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(install_service)}\""),
            # "remove_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(remove_service)}\""),
        },
    )
