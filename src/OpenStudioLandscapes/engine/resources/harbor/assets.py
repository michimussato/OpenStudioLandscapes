import configparser
import copy
import os
import pathlib
import shutil
import textwrap
from pathlib import Path
from typing import Generator, List, Any

import requests
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MaterializeResult,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *
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
def LIBRARY_DELETED(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
) -> Generator[Output[requests.PreparedRequest] | AssetMaterialization, None, None]:

    # harbor_up = harbor_resource.harbor_up()
    #
    # if harbor_up:
    #     raise OpenStudioLandscapesException("Could not start Harbor")
    # # else:
    # #     ret = harbor_resource.proc

    library_exists_response = harbor_resource.query_project_exists(
        project_name="library",
    )

    library_exists = library_exists_response.status_code == requests.status_codes.codes.NOT_FOUND

    context.log.info(f"Library exists: {library_exists_response}")

    delete_libraray_request = harbor_resource.delete_project_prepared_request(
        project_name="library",
    )

    yield Output(delete_libraray_request)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.bool(library_exists),
            "library_exists_response": MetadataValue.text(f"{library_exists_response = }"),
            "delete_libraray_request_url": MetadataValue.text(delete_libraray_request.url),
        },
    )


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
def OPENSTUDIOLANDSCAPES_EXISTS(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
) -> Generator[Output[requests.PreparedRequest] | AssetMaterialization, None, None]:

    # harbor_up = harbor_resource.harbor_up()
    #
    # if harbor_up:
    #     raise OpenStudioLandscapesException("Could not start Harbor")
    # # else:
    # #     ret = harbor_resource.proc

    project_name = "openstudiolandscapes"

    project_exists_response = harbor_resource.query_project_exists(
        project_name=project_name,
    )

    project_exists = project_exists_response.status_code == requests.status_codes.codes.OK

    context.log.info(f"Project exists: {project_exists_response}")

    create_openstudiolandscapes_request = harbor_resource.delete_project_prepared_request(
        project_name=project_name,
    )

    yield Output(create_openstudiolandscapes_request)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.bool(project_exists),
            "library_exists_response": MetadataValue.text(f"{project_exists_response = }"),
            "delete_libraray_request_url": MetadataValue.text(create_openstudiolandscapes_request.url),
        },
    )


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
def su_method(
        context: AssetExecutionContext,
) -> Generator[Output[list[str]] | AssetMaterialization, None, None]:

    su_methods = {
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
    }

    su_method = "pkexec"

    yield Output(su_methods[su_method])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(su_methods[su_method]),
            "su_methods": MetadataValue.json(su_methods),
            "su_method": MetadataValue.text(su_method),
        },
    )


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
def HARBOR_COMMANDS(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
) -> MaterializeResult:

    return MaterializeResult(
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
            # "library_exists": MetadataValue.text(f"{library_exists.status_code = }"),
            # "project_exists": MetadataValue.text(f"{project_exists.status_code = }"),
            # "random_exists": MetadataValue.text(f"{random_exists.status_code = }"),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "su_method": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "su_method"])),
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
def HARBOR_RESET(
        context: AssetExecutionContext,
        su_method: list[str],
        # harbor_resource: HarborResource,
        # env: dict,  # pylint: disable=redefined-outer-name
) -> MaterializeResult:

    d_ = expand_dict_vars(
        dict_to_expand=copy.deepcopy(os.environ),
        kv=os.environ,
    )

    harbor_root_dir: pathlib.Path = pathlib.Path(
        d_['OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR']
    )

    git_clean = [
        shutil.which("git"),
        "clean",
        "-x",
        "--force",
        harbor_root_dir.as_posix(),
    ]

    # su_method = {
    #     "su": [
    #         shutil.which("su"),
    #         "-",
    #         "root",
    #     ],
    #     "sudo": [
    #         shutil.which("sudo"),
    #         "--user=root",
    #     ],
    #     "pkexec": [
    #         shutil.which("pkexec"),
    #     ],
    # }["pkexec"]

    sudo_bash_c = [
        *su_method,
        shutil.which("bash"),
        "-c",
    ]

    return MaterializeResult(
        asset_key=context.asset_key,
        metadata={
            "git_clean": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(git_clean)}\""),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
        "su_method": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "su_method"])),
    },
    deps=[
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_PREPARE"]),
        # AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "harbor_popen"]),
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
def HARBOR_SYSTEMD(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
        env: dict,  # pylint: disable=redefined-outer-name
        su_method: list[str],  # pylint: disable=redefined-outer-name
) -> MaterializeResult:

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

    sudo_bash_c = [
        *su_method,
        shutil.which("bash"),
        "-c",
    ]

    return MaterializeResult(
        asset_key=context.asset_key,
        metadata={
            "install_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(install_service)}\""),
            "remove_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(remove_service)}\""),
            "journald": MetadataValue.path(f"{' '.join(journalctl)}"),
            "unit": MetadataValue.path(unit_file),
            "unit_dict": MetadataValue.json(unit_dict),
            unit_file.name: MetadataValue.md(f"```shell\n{unit_file_content}\n```"),
            # "journald": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(journalctl)}\""),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    # ins={
    #     "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
    # },
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
def HARBOR_PREPARE(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
        # env: dict,  # pylint: disable=redefined-outer-name
) -> MaterializeResult:

    # harbor_root_dir: pathlib.Path = pathlib.Path(
    #     f"{os.environ['OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR']}".format(
    #         **os.environ,
    #         **env,
    #     )
    # )

    # su_method = {
    #     "su": [
    #         shutil.which("su"),
    #         "-",
    #         "root",
    #     ],
    #     "sudo": [
    #         shutil.which("sudo"),
    #         "--user=root",
    #     ],
    #     "pkexec": [
    #         shutil.which("pkexec"),
    #     ],
    # }["pkexec"]

    # sudo_bash_c = [
    #     *su_method,
    #     shutil.which("bash"),
    #     "-c",
    # ]

    prepare: List = harbor_resource.harbor_prepare(context=context)

    return MaterializeResult(
        asset_key=context.asset_key,
        metadata={
            # "__".join(context.asset_key.path): MetadataValue.path(unit_file),
            # "unit_dict": MetadataValue.json(unit_dict),
            # unit_file.name: MetadataValue.md(f"```shell\n{unit_file_content}\n```"),
            "prepare": MetadataValue.path(f"{' '.join(prepare)}"),
            # "git_clean": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(git_clean)}\""),
            # "install_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(install_service)}\""),
            # "remove_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(remove_service)}\""),
        },
    )
