import configparser
import copy
import json
import os
import pathlib
import shutil
import tarfile
import textwrap
from pathlib import Path
from typing import Generator, List, Any

import requests
import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MaterializeResult,
    MetadataValue,
    Output,
    asset, EnvVar,
)

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.resources.harbor.constants import *
from OpenStudioLandscapes.engine.exceptions import OpenStudioLandscapesException

from OpenStudioLandscapes.engine.resources.harbor.resources import HarborResource


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    deps=[
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_SYSTEMD"]),
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_COMMANDS"]),
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

    project_name = "library"

    library_exists_response = harbor_resource.query_project_exists(
        project_name=project_name,
    )

    library_exists = library_exists_response.status_code == requests.status_codes.codes.OK

    context.log.info(f"Library exists: {library_exists_response}")

    delete_libraray_request = harbor_resource.delete_project_prepared_request(
        project_name=project_name,
    )

    if library_exists:
        raise OpenStudioLandscapesException(
            f"Project {project_name} does exist. Delete it first."
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
    deps=[
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_SYSTEMD"]),
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_COMMANDS"]),
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

    if not project_exists:
        raise OpenStudioLandscapesException(
            f"Project {project_name} does not exist. Create it first."
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
def shell(
        context: AssetExecutionContext,
) -> Generator[Output[list[str]] | AssetMaterialization, None, None]:

    shell = [
        shutil.which("bash"),
        "-c",
    ]

    yield Output(shell)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(shell),
            # "shell": MetadataValue.json(shell),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "su_method": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "su_method"])),
        "shell": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "shell"])),
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
def HARBOR_COMMANDS(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
        su_method: list[str],
        shell: list[str],
) -> MaterializeResult:

    harbor_up = harbor_resource._cmd_harbor_up(detach=False)
    harbor_up_detach = harbor_resource._cmd_harbor_up(detach=True)
    harbor_down = harbor_resource._cmd_harbor_down()
    harbor_restart = harbor_resource._cmd_harbor_restart()
    harbor_ps = harbor_resource._cmd_harbor_ps()

    return MaterializeResult(
        asset_key=context.asset_key,
        metadata={
            "harbor_up": MetadataValue.path(f"{' '.join(su_method + shell)} \"{' '.join(harbor_up)}\""),
            "harbor_up_detach": MetadataValue.path(f"{' '.join(su_method + shell)} \"{' '.join(harbor_up_detach)}\""),
            "harbor_down": MetadataValue.path(f"{' '.join(su_method + shell)} \"{' '.join(harbor_down)}\""),
            "harbor_restart": MetadataValue.path(f"{' '.join(su_method + shell)} \"{' '.join(harbor_restart)}\""),
            "harbor_ps": MetadataValue.path(f"{' '.join(shell)} \"{' '.join(harbor_ps)}\""),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    deps=[
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_SYSTEMD"]),
        AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_COMMANDS"]),
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
def HARBOR_HEALTH(
        context: AssetExecutionContext,
        harbor_resource: HarborResource,
) -> MaterializeResult:

    return MaterializeResult(
        asset_key=context.asset_key,
        metadata={
            "systeminfo": MetadataValue.json(harbor_resource.systeminfo().json()),
            "systeminfo_volumes": MetadataValue.json(harbor_resource.systeminfo_volumes().json()),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "su_method": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "su_method"])),
        "shell": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "shell"])),
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
        shell: list[str],
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

    sudo_bash_c = [
        *su_method,
        *shell,
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

    # DOWNLOAD

    # SETUP

    # WRITE YAML

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
def HARBOR_DOWNLOAD(
        context: AssetExecutionContext,
        # harbor_resource: HarborResource,
        # env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path | Any] | AssetMaterialization | Any, Any, MaterializeResult]:

    d_ = expand_dict_vars(
        dict_to_expand=copy.deepcopy(os.environ),
        kv=os.environ,
    )

    harbor_root_dir: pathlib.Path = pathlib.Path(d_["OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR"])
    harbor_root_dir.mkdir(parents=True, exist_ok=True)

    dest_folder = harbor_root_dir / d_["OPENSTUDIOLANDSCAPES__HARBOR_DOWNLOAD_DIR"]
    dest_folder.mkdir(parents=True, exist_ok=True)

    url = d_["OPENSTUDIOLANDSCAPES__HARBOR_INSTALLER_ONLINE"]

    if not dest_folder.exists():
        dest_folder.mkdir(
            parents=True, exist_ok=True
        )  # create folder if it does not exist

    tar_filename = url.split("/")[-1].replace(" ", "_")  # be careful with file names
    tar_file_path = dest_folder / tar_filename

    r = requests.get(url, stream=True)
    if r.ok:
        context.log.info("Saving to %s" % tar_file_path.absolute().as_posix())
        with open(tar_file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
        # return file_path

        yield Output(tar_file_path)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.path(tar_file_path),
                # "harbor_yml": MetadataValue.md(f"```shell\n{harbor_yml}\n```"),
                "d_": MetadataValue.json(dict(d_)),
            },
        )

    else:  # HTTP status code 4XX/5XX
        raise Exception(
            "Download failed: status code {}\n{}".format(r.status_code, r.text)
        )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "HARBOR_DOWNLOAD": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_DOWNLOAD"])),
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
def HARBOR_EXTRACT(
        context: AssetExecutionContext,
        HARBOR_DOWNLOAD: pathlib.Path,
        # harbor_resource: HarborResource,
        # env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Path | Any] | AssetMaterialization | Any, Any, MaterializeResult]:

    d_ = expand_dict_vars(
        dict_to_expand=copy.deepcopy(os.environ),
        kv=os.environ,
    )

    harbor_root_dir: pathlib.Path = pathlib.Path(d_["OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR"])
    harbor_root_dir.mkdir(parents=True, exist_ok=True)

    dest_folder = harbor_root_dir / d_["OPENSTUDIOLANDSCAPES__HARBOR_DOWNLOAD_DIR"]
    dest_folder.mkdir(parents=True, exist_ok=True)

    harbor_bin_dir: pathlib.Path = (
            harbor_root_dir / d_["OPENSTUDIOLANDSCAPES__HARBOR_BIN_DIR"]
    )
    harbor_bin_dir.mkdir(parents=True, exist_ok=True)

    prepare: pathlib.Path = harbor_bin_dir / "prepare"

    # url = d_["OPENSTUDIOLANDSCAPES__HARBOR_INSTALLER_ONLINE"]

    # equivalent to tar --strip-components=1
    # Credits: https://stackoverflow.com/a/78461535
    strip1 = lambda member, path: member.replace(
        name=pathlib.Path(*pathlib.Path(member.path).parts[1:])
    )

    context.log.debug("Extracting tar file...")
    with tarfile.open(HARBOR_DOWNLOAD, "r:gz") as tar:
        tar.extractall(
            path=harbor_bin_dir,
            filter=strip1,
        )
    context.log.debug("All files extracted to %s" % harbor_bin_dir.as_posix())

    yield Output(harbor_bin_dir)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(harbor_bin_dir),
            # "harbor_yml": MetadataValue.md(f"```shell\n{harbor_yml}\n```"),
            "d_": MetadataValue.json(dict(d_)),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    # ins={
    #     "env": AssetIn(AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"])),
    # },
    # deps=[
    #     AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_EXTRACT"])
    # ],
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
def HARBOR_CONSTRUCT_CONFIG(
        context: AssetExecutionContext,
        # harbor_resource: HarborResource,
        # env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

    context.log.warning(os.environ)
    # context.log.warning(env)

    d_ = expand_dict_vars(
        dict_to_expand=copy.deepcopy(os.environ),
        kv=os.environ,
    )

    harbor_root_dir: pathlib.Path = pathlib.Path(d_["OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR"])
    harbor_root_dir.mkdir(parents=True, exist_ok=True)

    # harbor_root_dir: pathlib.Path = pathlib.Path(d_["OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR"])
    # harbor_root_dir.mkdir(parents=True, exist_ok=True)

    harbor_data_dir = harbor_root_dir / d_["OPENSTUDIOLANDSCAPES__HARBOR_DATA_DIR"]
    harbor_data_dir.mkdir(parents=True, exist_ok=True)

    harbor_dict = {
        "hostname": d_["OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME"],
        "http": {"port": d_["OPENSTUDIOLANDSCAPES__HARBOR_PORT"]},
        "harbor_admin_password": EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD").get_value(),
        "database": {
            "password": "root123",
            "max_idle_conns": 100,
            "max_open_conns": 900,
            "conn_max_idle_time": 0,
        },
        "data_volume": harbor_data_dir.as_posix(),
        "trivy": {
            "ignore_unfixed": False,
            "skip_update": False,
            "skip_java_db_update": False,
            "offline_scan": False,
            "security_check": "vuln",
            "insecure": False,
            "timeout": "5m0s",
        },
        "jobservice": {
            "max_job_workers": 10,
            "job_loggers": ["STD_OUTPUT", "FILE"],
            "logger_sweeper_duration": 1,
        },
        "notification": {
            "webhook_job_max_retry": 3,
            "webhook_job_http_client_timeout": 3,
        },
        "log": {
            "level": "info",
            "local": {
                "rotate_count": 50,
                "rotate_size": "200M",
                "location": "/var/log/harbor",
            },
        },
        "_version": "2.12.0",
        "proxy": {
            "http_proxy": None,
            "https_proxy": None,
            "no_proxy": None,
            "components": ["core", "jobservice", "trivy"],
        },
        "upload_purging": {
            "enabled": True,
            "age": "168h",
            "interval": "24h",
            "dryrun": False,
        },
        "cache": {"enabled": False, "expire_hours": 24},
    }

    harbor_yml: str = yaml.dump(
        harbor_dict,
        indent=2,
    )

    # context.log.warning(d_)

    yield Output(harbor_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(
                harbor_dict
            ),
            "harbor_yml": MetadataValue.md(f"```shell\n{harbor_yml}\n```"),
            "d_": MetadataValue.json(dict(d_)),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "HARBOR_CONSTRUCT_CONFIG": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_CONSTRUCT_CONFIG"])),
        "HARBOR_EXTRACT": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_EXTRACT"])),
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
def HARBOR_WRITE_CONFIG(
        context: AssetExecutionContext,
        HARBOR_CONSTRUCT_CONFIG: dict,  # pylint: disable=redefined-outer-name
        HARBOR_EXTRACT: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

    d_ = expand_dict_vars(
        dict_to_expand=copy.deepcopy(os.environ),
        kv=os.environ,
    )

    harbor_root_dir: pathlib.Path = pathlib.Path(d_["OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR"])
    harbor_root_dir.mkdir(parents=True, exist_ok=True)

    # harbor_bin_dir: pathlib.Path = (
    #         harbor_root_dir / d_["OPENSTUDIOLANDSCAPES__HARBOR_BIN_DIR"]
    # )
    HARBOR_EXTRACT.mkdir(parents=True, exist_ok=True)

    yaml_out: pathlib.Path = HARBOR_EXTRACT / "harbor.yml"

    harbor_yml: str = yaml.dump(
        HARBOR_CONSTRUCT_CONFIG,
        indent=2,
    )

    with open(yaml_out, "w") as fw:
        fw.write(harbor_yml)

    yield Output(yaml_out)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(
                yaml_out
            ),
            "HARBOR_CONSTRUCT_CONFIG": MetadataValue.json(HARBOR_CONSTRUCT_CONFIG),
            "harbor_yml": MetadataValue.md(f"```shell\n{harbor_yml}\n```"),
            "d_": MetadataValue.json(dict(d_)),
        },
    )


@asset(
    **ASSET_HEADER_RESOURCE_HARBOR,
    ins={
        "shell": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "shell"])),
        "HARBOR_EXTRACT": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_EXTRACT"])),
        "HARBOR_WRITE_CONFIG": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_WRITE_CONFIG"])),
        # "HARBOR_EXTRACT": AssetIn(AssetKey([*ASSET_HEADER_RESOURCE_HARBOR["key_prefix"], "HARBOR_EXTRACT"])),
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
def HARBOR_PREPARE(
        context: AssetExecutionContext,
        # HARBOR_CONSTRUCT_CONFIG: dict,  # pylint: disable=redefined-outer-name
        shell: list[str],  # pylint: disable=redefined-outer-name
        HARBOR_EXTRACT: pathlib.Path,  # pylint: disable=redefined-outer-name
        HARBOR_WRITE_CONFIG: pathlib.Path,  # pylint: disable=redefined-outer-name
) -> Generator[Output[Any] | AssetMaterialization | Any, Any, None]:

    d_ = expand_dict_vars(
        dict_to_expand=copy.deepcopy(os.environ),
        kv=os.environ,
    )

    # harbor_root_dir: pathlib.Path = pathlib.Path(d_["OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR"])
    # harbor_root_dir.mkdir(parents=True, exist_ok=True)

    # harbor_bin_dir: pathlib.Path = (
    #         harbor_root_dir / d_["OPENSTUDIOLANDSCAPES__HARBOR_BIN_DIR"]
    # )
    # HARBOR_EXTRACT.mkdir(parents=True, exist_ok=True)

    # yaml_out: pathlib.Path = HARBOR_EXTRACT / "harbor.yml"

    # harbor_yml: pathlib.Path = write_harbor_yml(
    #     yaml_out=harbor_bin_dir / "harbor.yml",
    # )

    if not HARBOR_WRITE_CONFIG.exists():
        raise FileNotFoundError("`harbor.yml` file not found. " "Not able to continue.")

    prepare: pathlib.Path = HARBOR_EXTRACT / "prepare"

    if not prepare.exists():
        raise FileNotFoundError("`prepare` file not found. " "Not able to continue.")

    context.log.debug("Preparing Harbor...")

    bash_c = [
        # *su_method,
        *shell,
    ]

    cmd_prepare = [
        prepare.as_posix(),
    ]

    yield Output(prepare)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(
                prepare
            ),
            "prepare": MetadataValue.path(f"{' '.join(bash_c)} \"{' '.join(cmd_prepare)}\""),
            # "HARBOR_CONSTRUCT_CONFIG": MetadataValue.json(HARBOR_CONSTRUCT_CONFIG),
            # "harbor_yml": MetadataValue.md(f"```shell\n{harbor_yml}\n```"),
            "d_": MetadataValue.json(dict(d_)),
        },
    )

    # DOWNLOAD

    # SETUP

    # WRITE YAML



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

    # prepare: List = harbor_resource.harbor_prepare(context=context)
    #
    # return MaterializeResult(
    #     asset_key=context.asset_key,
    #     metadata={
    #         # "__".join(context.asset_key.path): MetadataValue.path(unit_file),
    #         # "unit_dict": MetadataValue.json(unit_dict),
    #         # unit_file.name: MetadataValue.md(f"```shell\n{unit_file_content}\n```"),
    #         "prepare": MetadataValue.path(f"{' '.join(prepare)}"),
    #         # "git_clean": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(git_clean)}\""),
    #         # "install_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(install_service)}\""),
    #         # "remove_service": MetadataValue.path(f"{' '.join(sudo_bash_c)} \"{' '.join(remove_service)}\""),
    #     },
    # )
