import getpass
import pathlib
import socket
import yaml
import json
import tempfile
import textwrap
import uuid
from datetime import datetime
from typing import Generator, MutableMapping
from pydantic_core._pydantic_core import ValidationError

import pytz
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

from OpenStudioLandscapes.engine import exceptions
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.config.models import ConfigEngine, CONFIG_STR
import OpenStudioLandscapes.engine.discovery.discovery as discovery


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
        "LANDSCAPE": f"{datetime.strftime(now, '%Y-%m-%d_%H-%M-%S')}__{uuid.uuid4().hex}".replace(
            "__", "_"
        ).replace(
            "_", "-"
        ),
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
    ins={
        "env": AssetIn(
            AssetKey([*ASSET_HEADER_BASE_ENV["key_prefix"], "env"]),
        ),
    },
    description=textwrap.dedent(
        f"""
Reads options from a custom `config.yml`.
If the custom `config.yml` does not exist, it 
will be created locally containing default options.

---

For reference, the default `config.yml` looks as follows:
        
```yaml
{CONFIG_STR}
```
"""
    )
)
def CONFIG(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[
    Output[ConfigEngine]
    | AssetMaterialization,
    None,
    None,
]:

    # config_default_ = yaml.safe_load(CONFIG_STR)

    # This is valid as we checked it already
    # config_base = ConfigEngine(**config_default_)

    # # https://jsschools.com/python/5-powerful-python-libraries-for-efficient-file-han/
    # config_yml_object = config_base.openstudiolandscapes__configstore_root.expanduser().resolve() / dist.name / "config.yml"
    # if not config_yml_object.exists():
    #     config_yml_object.parent.mkdir(parents=True, exist_ok=True)
    #     config_yml_object.touch(exist_ok=True)
    #     config_yml_object.write_text(CONFIG_STR)
    # config_dict: dict = yaml.safe_load(config_yml_object.read_text())

    # context.log.error(f"{config_dict = }")
    # config_dict = {'openstudiolandscapes__repository_root': '{REPOSITORY_ROOT}', 'openstudiolandscapes__configstore_root': '~/.config/OpenStudioLandscapes/config-store', 'openstudiolandscapes__domain_lan': 'openstudiolandscapes.lan', 'openstudiolandscapes__docker_config': {'use_registry': True, 'docker_registry_config': {'docker_push': True, 'docker_pull': True, 'docker_repository_name': 'OpenStudioLandscapes', 'docker_registry_fqdn': 'registry.openstudiolandscapes.lan', 'docker_registry_username': 'registry-user', 'docker_registry_password': 'registry-password'}}, 'illegal_option': 1234}
    # context.log.error(f"{env = }")
    # env = {'GIT_ROOT': '/home/michael/git/repos/OpenStudioLandscapes', 'DOT_LANDSCAPES': '/home/michael/git/repos/OpenStudioLandscapes/.landscapes', 'DOT_SHARED_VOLUMES': '.shared_volumes', 'DOT_FEATURES': '/home/michael/git/repos/OpenStudioLandscapes/.features', 'DOT_OVERRIDES': '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-12-09-03-03-05-32bc816edf7f49438b6a19030e82d0dc/.overrides', 'AUTHOR': 'michimussato@gmail.com', 'CREATED_BY': 'michael', 'CREATED_ON': 'lenovo', 'CREATED_AT': '2025-12-09_03-03-11', 'TIMEZONE': 'Europe/Zurich', 'DEFAULT_CONFIG_DBPATH': '/data/configdb', 'PYTHON_MAJ': '3', 'PYTHON_MIN': '11', 'PYTHON_PAT': '11', 'LANDSCAPE': '2025-12-09-03-03-05-32bc816edf7f49438b6a19030e82d0dc'}

    # config_store_validated.model_dump(mode="python")

    # config_expanded = expand_dict_vars(
    #     dict_to_expand=config_dict.copy(),
    #     kv=env,
    # )

    config_validated = discovery.get_config_engine()

    # try:
    #     context.log.info(f"Validating: {config_expanded = }")
    #     config_validated = ConfigEngine(**config_expanded)
    #     context.log.debug(f"Validated.")
    # except ValidationError as err:
    #     context.log.error(
    #         "Config Validation failed. "
    #         f"The parsed config for "
    #         f"{dist.name} contains "
    #         "errors, missing and/or illegal parameters."
    #     )
    #     raise ValidationError from err

    yield Output(config_validated)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.md(f"```json\n{json.dumps(config_validated.model_dump(mode='json'), indent=2, default=str)}\n```"),
            # "config_yml_path": MetadataValue.path(config_yml_object),
            # "config_dict": MetadataValue.md(f"```json\n{json.dumps(config_dict, indent=2, default=str)}\n```"),
            # "config_dict_expanded": MetadataValue.md(f"```json\n{json.dumps(config_expanded, indent=2, default=str)}\n```"),
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
    # Todo
    #  - [ ] Move to constants.py
    tz = get_str_env(
        env="CONTAINER_TIMEZONE",
        default="Europe/Zurich",
    )

    if tz not in pytz.all_timezones:
        raise Exception(f"Unknown container timezone: {tz}")

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
        "CREATED_AT": str(datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")),
        # Todo
        #  - [ ] move TIMEZONE to config.yml
        "TIMEZONE": str(tz),
        # "IMAGE_PREFIX": "michimussato",
        # Todo:
        #  - [ ] Where is this being used?
        "DEFAULT_CONFIG_DBPATH": "/data/configdb",
        # "OPENSTUDIOLANDSCAPES__DOMAIN_LAN": EnvVar(
        #     "OPENSTUDIOLANDSCAPES__DOMAIN_LAN"
        # ).get_value(),
        # "OPENSTUDIOLANDSCAPES__DOMAIN_WAN": EnvVar(
        #     "OPENSTUDIOLANDSCAPES__DOMAIN_WAN"
        # ).get_value(),
        # https://vfxplatform.com/
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
