import os
import shutil
import subprocess

from dagster.dagster_shared.shared import helpers

from dagster import (AssetExecutionContext,
                     asset,
                     Output,
                     AssetMaterialization,
                     MetadataValue,
                     AssetIn)


# @asset
# def my_skeleton_package_assets(
#     context: AssetExecutionContext,
# ) -> None:
#     return None


@asset
def env(
        context: AssetExecutionContext,
) -> dict:
    _env: dict = {
        "MONGO_EXPRESS_PORT_HOST": 8080,
        "MONGO_EXPRESS_PORT_CONTAINER": 8081,
        "MONGO_DB_NAME": "deadline10db",

        "LIKEC4_DEV_PORT_HOST": 4567,
        "LIKEC4_DEV_PORT_CONTAINER": 4567,

        "FILEBROWSER_PORT_HOST": 86,
        "FILEBROWSER_PORT_CONTAINER": 80,

        "DAGSTER_DEV_PORT_HOST": 3003,
        "DAGSTER_DEV_PORT_CONTAINER": 3006,
        "DAGSTER_HOME": "/dagster/materializations",
        "DAGSTER_WORKSPACE": "/dagster/workspace.yaml",

        "DEADLINE_VERSION": "10.2.1.1",

        "RCS_HTTP_PORT_HOST": 8888,
        "RCS_HTTP_PORT_CONTAINER": 8888,

        "WEBSERVICE_HTTP_PORT_HOST": 8899,
        "WEBSERVICE_HTTP_PORT_CONTAINER": 8899,

        "MONGO_DB_PORT_HOST": 21017,
        "MONGO_DB_PORT_CONTAINER": 21017,
        "MONGO_PORT": "${MONGO_DB_PORT_CONTAINER}",
        # https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/#additional-information-1
        "ME_CONFIG_BASICAUTH_USERNAME": "web",
        "ME_CONFIG_BASICAUTH_PASSWORD": "web",
        "ME_CONFIG_OPTIONS_EDITORTHEME": "darcula",
        "ME_CONFIG_MONGODB_SERVER": "mongodb-10-2",
        "ME_CONFIG_MONGODB_URL": "mongodb://admin:pass@localhost:${MONGO_DB_PORT_CONTAINER}/db?ssl=false",

        "AYON_PORT_HOST": 5005,
        "AYON_PORT_CONTAINER": 5000,

        "KITSU_PORT_HOST": 8181,
        "KITSU_PORT_CONTAINER": 80,
        #"SECRETS_USERNAME": "SecretsAdmin",
        #"SECRETS_PASSWORD": "%ecretsPassw0rd!",
        "ROOT_DOMAIN": "farm.evil",
        "DB_HOST": "mongodb-10-2",

        "GOOGLE_API_KEY": "AIzaSyBBH8zUH4VC1Bov-3EdVbjG0gBauroMd9E",
        "GOOGLE_ID": "1VZhCcxvCAc4oozLAKRCv_zwQLMuVdMRz",

        "PYTHON_VERSION": "3.11.11",
        "PYTHON_MAJ": 3,
        "PYTHON_MIN": 11,
        "PYTHON_PAT": 11,

        "NFS_ENTRY_POINT": "/data/share/nfs",
        "NFS_ENTRY_POINT_LNS": "/nfs",
        "INSTALLERS_ROOT": "${NFS_ENTRY_POINT}/installers",

        # TODO
        # DEADLINE_INI:
        # DEADLINE_CLIENT_DIR: "/opt/Thinkbox/Deadline10"
        # DEADLINE_REPO_DIR: "/opt/Thinkbox/DeadlineRepository10"
        # MONGO_DB_NAME: deadline10db
        # MONGO_DB_HOST: $DB_HOST
        # MONGO_DB_PROD:
        # MONGO_DB_TEST:
    }

    yield Output(_env)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            context.asset_key.path[0]: MetadataValue.json(_env),
        },
    )

    return _env


@asset(
    ins={
        "env": AssetIn(),
    },
)
def build_repo_image(
        context: AssetExecutionContext,
        env: dict,
):
    cmd = list()

    cmd.append(shutil.which("ls"))
    cmd.append("-al")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            **os.environ,
            **env,
        }
    )

    handles = (proc.stdout, proc.stderr)
    labels = ("stdout", "stderr")
    functions = (context.log.info, context.log.warning)
    logs = helpers.iterate_fds(
        handles=handles,
        labels=labels,
        functions=functions,
        live_print=False,
    )

    metadata = dict()

    for _label, _function in zip(labels, functions):
        if bool(logs[_label]):
            _function(logs[_label].decode("utf-8"))
        metadata[_label] = MetadataValue.md(f"```shell\n{logs[_label].decode('utf-8')}\n```")

    yield Output(logs)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "cmd": MetadataValue.md(f"```shell\n{' '.join(cmd)}\n```"),
            **metadata,
        },
    )
