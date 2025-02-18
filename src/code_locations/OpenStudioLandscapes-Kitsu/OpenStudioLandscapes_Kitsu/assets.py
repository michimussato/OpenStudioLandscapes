import copy
import json
import pathlib
import shutil
import subprocess
import textwrap
import time
import urllib.parse
from typing import Generator

import yaml
from python_on_whales import docker

from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    MaterializeResult,
    MetadataValue,
    Output,
    asset,
    AssetsDefinition,
)
from OpenStudioLandscapes.engine.base.assets import KEY as KEY_BASE
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.base.ops import op_docker_compose_graph
from OpenStudioLandscapes.engine.base.ops import op_group_out

"""
# cat /opt/zou/init_zou.sh
#!/bin/bash
export LC_ALL=C.UTF-8
export LANG=C.UTF-8

service postgresql start
service redis-server start

. /opt/zou/env/bin/activate

zou upgrade-db
zou init-data
zou create-admin admin@example.com --password mysecretpassword

service postgresql stop
service redis-server stop



/opt/zou# cat start_zou.sh
#!/bin/bash

# create /var/run/postgresql
. /usr/share/postgresql-common/init.d-functions
create_socket_directory

echo Running Zou...
supervisord -c /etc/supervisord.conf




# Upgrade DB
zou upgrade_db
"""


GROUP = "Kitsu"
KEY = "Kitsu"

asset_header = {"group_name": GROUP, "key_prefix": [KEY], "compute_kind": "python"}


@asset(
    **asset_header,
    ins={
        "group_in": AssetIn(
            AssetKey([KEY_BASE, "group_out"])
        ),
    },
)
def env(
    context: AssetExecutionContext,
    group_in: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:

    env_in = copy.deepcopy(group_in["env"])

    # @formatter:off
    _env = {
        # Todo:
        #  - [ ] These have no effect yet
        # "KITSU_ADMIN_USER": "admin@example.com",
        # "KITSU_ADMIN_PASSWORD": "mysecretpassword",
        "KITSU_PORT_HOST": "4545",
        "KITSU_PORT_CONTAINER": "80",
        "KITSU_DATABASE_INSTALL_DESTINATION": {
            #################################################################
            # Kitsu Postgresql DB will be created in (hardcoded):
            # "KITSU_DATABASE_INSTALL_DESTINATION" / "postgresql" / "14" / "main"
            # Kitsu Previews folder will be created in (hardcoded):
            # "KITSU_DATABASE_INSTALL_DESTINATION" / "previews"
            #################################################################
            #################################################################
            # Inside Landscape:
            "default": pathlib.Path(
                env_in["DOT_LANDSCAPES"],
                env_in.get("LANDSCAPE", "default"),
                "data",
                "kitsu",
            ).as_posix(),
            #################################################################
            # Prod DB:
            "prod_db": pathlib.Path(
                env_in["NFS_ENTRY_POINT"],
                "services",
                "kitsu",
            ).as_posix(),
            #################################################################
            # Test DB:
            "test_db": pathlib.Path(
                env_in["NFS_ENTRY_POINT"],
                "test_data",
                "10.2",
                "kitsu",
            ).as_posix(),
        }["default"],
        f"KITSU_INIT_ZOU": pathlib.Path(
            env_in["DOT_LANDSCAPES"],
            env_in.get("LANDSCAPE", "default"),
            "configs",
            "kitsu",
            "init_zou.sh",
        )
        .expanduser()
        .as_posix(),
        f"KITSU_TEMPLATE_DB_14": pathlib.Path(
            env_in["CONFIGS_ROOT"], "kitsu", "postgres", "template_dbs", "14", "main"
        )
        .expanduser()
        .as_posix(),
    }
    # @formatter:on

    env_in.update(_env)

    env_json = pathlib.Path(
        env_in["DOT_LANDSCAPES"],
        env_in.get("LANDSCAPE", "default"),
        "third_party",
        *context.asset_key.path,
        f"{'__'.join(context.asset_key.path)}.json",
    )

    env_json.parent.mkdir(parents=True, exist_ok=True)

    with open(env_json, "w") as fw:
        json.dump(
            obj=_env.copy(),
            fp=fw,
            indent=2,
            ensure_ascii=True,
            sort_keys=True,
        )

    yield Output(env_in)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(env_in),
            "json": MetadataValue.path(env_json),
        },
    )


@asset(
    **asset_header,
)
def apt_packages(
    context: AssetExecutionContext,
) -> Generator[Output[dict[str, list[str]]] | AssetMaterialization, None, None]:
    """ """

    _apt_packages = dict()

    _apt_packages["base"] = [
        "htop",
        "curl",
    ]

    yield Output(_apt_packages)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(_apt_packages),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
        "apt_packages": AssetIn(
            AssetKey([KEY, "apt_packages"]),
        ),
    },
)
def build_docker_image(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    apt_packages: dict[str, list[str]],  # pylint: disable=redefined-outer-name
) -> Generator[Output[str] | AssetMaterialization, None, None]:
    """ """

    docker_file = pathlib.Path(
        env["DOT_LANDSCAPES"],
        env.get("LANDSCAPE", "default"),
        KEY,
        "__".join(context.asset_key.path),
        "Dockerfiles",
        "Dockerfile",
    )

    tags = [
        f"{env.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:latest",
        f"{env.get('IMAGE_PREFIX')}/{'__'.join(context.asset_key.path).lower()}:{env.get('LANDSCAPE', str(time.time()))}",
    ]

    apt_install_str_base: str = get_apt_install_str(
        apt_install_packages=apt_packages["base"],
    )

    # @formatter:off
    docker_file_str = textwrap.dedent(
        """
        # {auto_generated}
        # {dagster_url}
        # https://hub.docker.com/r/cgwire/cgwire
        FROM cgwire/cgwire:latest AS {image_name}
        LABEL authors="{AUTHOR}"

        SHELL ["/bin/bash", "-c"]

        ARG DEBIAN_FRONTEND=noninteractive

        ENV CONTAINER_TIMEZONE={TIMEZONE}
        ENV SET_CONTAINER_TIMEZONE=true

        RUN apt-get update && apt-get upgrade -y

        {apt_install_str_base}

        RUN apt-get clean

        WORKDIR /opt/zou

        ENTRYPOINT []
    """
    ).format(
        apt_install_str_base=apt_install_str_base,
        auto_generated=f"AUTO-GENERATED by Dagster Asset {'__'.join(context.asset_key.path)}",
        dagster_url=urllib.parse.quote(
            f"http://localhost:3000/asset-groups/{'%2F'.join(context.asset_key.path)}",
            safe=":/%",
        ),
        image_name="__".join(context.asset_key.path).lower(),
        **env,
    )
    # @formatter:on

    # Todo
    #  - [ ] WARN: StageNameCasing: Stage name 'Kitsu__build' should be lowercase (line 5)

    shutil.rmtree(docker_file.parent, ignore_errors=True)

    docker_file.parent.mkdir(parents=True, exist_ok=True)

    with open(docker_file, "w") as fw:
        fw.write(docker_file_str)

    with open(docker_file, "r") as fr:
        docker_file_content = fr.read()

    stream = docker.build(
        context_path=docker_file.parent.as_posix(),
        cache=DOCKER_USE_CACHE,
        tags=tags,
        stream_logs=True,
    )

    log: str = ""

    for msg in stream:
        context.log.debug(msg)
        log += msg

    cmds_docker = compile_cmds(
        docker_file=docker_file,
        tag=tags[1],
    )

    yield Output(tags[1])

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(tags[1]),
            "docker_file": MetadataValue.md(f"```shell\n{docker_file_content}\n```"),
            **cmds_docker,
            "build_logs": MetadataValue.md(f"```shell\n{log}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
    },
)
def script_prepare_db(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str]] | AssetMaterialization, None, None]:

    ret = dict()

    ret["exe"] = shutil.which("bash")
    ret["script"] = str()

    kitsu_db_dir_host = pathlib.Path(
        env.get("KITSU_DATABASE_INSTALL_DESTINATION"),
        "postgresql",
        "14",
        "main",
    )

    # sudo chown 105:105 KitsuPostgres
    # Concept: /usr/bin/sshpass -eENV_VAR /usr/bin/ssh "echo $ENV_VAR | sudo -S <cmd>"
    # Because shutil.chown cannot sudo
    # Requirements:
    # 2025-01-20 11:00:01.316 UTC [98] FATAL:  data directory "/var/lib/postgresql/14/main" has invalid permissions
    # 2025-01-20 11:00:01.316 UTC [98] DETAIL:  Permissions should be u=rwx (0700) or u=rwx,g=rx (0750).

    kitsu_postgres_uid: int = 105
    kitsu_postgres_gid: int = 105
    kitsu_postgres_chmod: int = [700, 750][1]

    """
    Reference Script:

    #!/bin/bash

    echo $SSH_PASS;
    echo $SSH_PASS;

    /usr/bin/sshpass -eSSH_PASS ssh -tt -oStrictHostKeyChecking=no michael@localhost << EOF
    echo ${SSH_PASS} | \
    sudo -S chown -R 105:105 /home/michael/git/repos/studio-landscapes/.landscapes/2025-01-27_09-38-08__98308581e4744378ae2972dadc88af1c/data/kitsu/postgresql/14/main && \
    sudo -S chmod 0750 /home/michael/git/repos/studio-landscapes/.landscapes/2025-01-27_09-38-08__98308581e4744378ae2972dadc88af1c/data/kitsu/postgresql/14/main && \
    exit 0;
    EOF

    echo $SSH_PASS;
    echo Success;
    exit 0;
    """

    # Todo:
    #  - [ ] ideally over SSH but it seems to be a PITA

    # @formatter:off
    ret["script"] += "#!/bin/bash\n"
    ret["script"] += "\n"
    # ret["script"] += "echo $SSH_PASS;\n"
    # ret["script"] += "echo $SSH_PASS;\n"
    # ret["script"] += "\n"
    # ret["script"] += f"{shutil.which('sshpass')} -eSSH_PASS ssh -tt -oStrictHostKeyChecking=no {env['SSH_USER']}@{env['SSH_HOST']} << 'EOF'\n"
    # ret["script"] += f"{shutil.which('sshpass')} -eSSH_PASS ssh -tt -oStrictHostKeyChecking=no {env['SSH_USER']}@{env['SSH_HOST']} << EOF\n"
    ret[
        "script"
    ] += f"echo $SUDO_PASS | sudo -S -k /usr/bin/chown -R {kitsu_postgres_uid}:{kitsu_postgres_gid} {kitsu_db_dir_host.as_posix()};\n"
    ret[
        "script"
    ] += f"echo $SUDO_PASS | sudo -S -k /usr/bin/chmod {str(kitsu_postgres_chmod).zfill(4)} {kitsu_db_dir_host.as_posix()};\n"
    # ret["script"] += f"sudo -S chmod {str(kitsu_postgres_chmod).zfill(4)} {kitsu_db_dir_host.as_posix()} && \\\n"
    # ret["script"] += "exit 0;\n"
    # ret["script"] += "EOF\n"

    # ret["script"] += f"{shutil.which('sshpass')} -eSSH_PASS ssh -tt -oStrictHostKeyChecking=no {env['SSH_USER']}@{env['SSH_HOST']} \"echo $SSH_PASS | sudo -S chown -R {kitsu_postgres_uid}:{kitsu_postgres_gid} {kitsu_db_dir_host.as_posix()} && exit 0;\";\n"
    # # ret["script"] += f"{shutil.which('sshpass')} -eSSH_PASS ssh -tt -oStrictHostKeyChecking=no {env['SSH_USER']}@{env['SSH_HOST']} \"echo $SSH_PASS | sudo -S touch {kitsu_db_dir_host.as_posix()}/hello &>/dev/null && echo $? || echo 1;\";\n"
    # ret["script"] += f"{shutil.which('sshpass')} -eSSH_PASS ssh -tt -oStrictHostKeyChecking=no {env['SSH_USER']}@{env['SSH_HOST']} \"echo $SSH_PASS | sudo -S chmod {str(kitsu_postgres_chmod).zfill(4)} {kitsu_db_dir_host.as_posix()} &>/dev/null && echo $? || echo 1; exit;;\";\n"
    ret["script"] += "\n"
    # ret["script"] += "echo $SSH_PASS;\n"
    ret["script"] += "echo Success;\n"
    ret["script"] += "exit 0;\n"
    # @formatter:on

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
            "script_prepare_db": MetadataValue.md(f"```shell\n{ret['script']}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
        "script_prepare_db": AssetIn(
            AssetKey([KEY, "script_prepare_db"]),
        ),
    },
)
def prepare_db(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    script_prepare_db: dict[str, str],  # pylint: disable=redefined-outer-name
):

    stdout_stderr = {
        "stdout": MetadataValue.md(f"```shell\nNone\n```"),
        "stderr": MetadataValue.md(f"```shell\nNone\n```"),
    }

    if not KITSUDB_INSIDE_CONTAINER:

        kitsu_db_dir_host = (
            pathlib.Path(env.get("KITSU_DATABASE_INSTALL_DESTINATION"))
            / "postgresql"
            / "14"
            / "main"
        )
        kitsu_db_dir_host.mkdir(parents=True, exist_ok=True)

        kitsu_db_template = env.get("KITSU_TEMPLATE_DB_14")

        try:
            empty = not any(kitsu_db_dir_host.iterdir())
        except PermissionError as e:
            context.log.warning(
                f"Database folder {kitsu_db_dir_host} already "
                f"exists and/or is not writable: "
                f"{e}"
            )
            empty = False

        if empty:
            shutil.copytree(
                src=kitsu_db_template,
                dst=kitsu_db_dir_host,
                dirs_exist_ok=True,
            )

        if bool(script_prepare_db["script"]):

            context.log.info(f"Setting ownership of {kitsu_db_dir_host.as_posix()}...")

            proc = subprocess.Popen(
                script_prepare_db["exe"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                env={
                    "SUDO_PASS": env["SUDO_PASS"],
                },
            )

            stdout, stderr = proc.communicate(
                input=script_prepare_db["script"].encode(),
            )

            stdout_stderr = {
                "stdout": MetadataValue.md(
                    f"```shell\n{stdout.decode(encoding='utf-8')}\n```"
                ),
                "stderr": MetadataValue.md(
                    f"```shell\n{stderr.decode(encoding='utf-8')}\n```"
                ),
            }

            # Todo:
            #  - [ ] implement reliable verification whether successful or not

    return MaterializeResult(
        asset_key=context.asset_key,
        metadata={
            **stdout_stderr,
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
    },
)
def script_init_zou(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict[str, str]] | AssetMaterialization, None, None]:
    """This script overrides the default
    Kitsu `/opt/zou/init_zou.sh` to be able
    to specify custom DB username and password"""

    # Todo
    #  - [ ] Custom username and password don't work yet

    ret = dict()

    ret["exe"] = shutil.which("bash")
    ret["script"] = str()

    # Source:
    # /opt/zou/init_zou.sh
    kitsu_admin_user = env.get("KITSU_ADMIN_USER", "admin@example.com")
    kitsu_admin_password = env.get("KITSU_ADMIN_PASSWORD", "mysecretpassword")

    ret["script"] += "#!/bin/bash\n"
    ret["script"] += "export LC_ALL=C.UTF-8\n"
    ret["script"] += "export LANG=C.UTF-8\n"
    ret["script"] += "\n"
    ret["script"] += "service postgresql start\n"
    ret["script"] += "service redis-server start\n"
    ret["script"] += "\n"
    ret["script"] += ". /opt/zou/env/bin/activate\n"
    ret["script"] += "\n"
    ret["script"] += "zou upgrade-db\n"
    ret["script"] += "zou init-data\n"
    ret[
        "script"
    ] += f"zou create-admin {kitsu_admin_user} --password {kitsu_admin_password}\n"
    ret["script"] += "\n"
    ret["script"] += "service postgresql stop\n"
    ret["script"] += "service redis-server stop\n"
    ret["script"] += "\n"
    ret["script"] += "echo Success\n"
    ret["script"] += "\n"
    ret["script"] += "exit 0\n"

    yield Output(ret)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(ret),
            "script_init_zou": MetadataValue.md(f"```shell\n{ret['script']}\n```"),
            "env": MetadataValue.json(env),
        },
    )


@asset(
    **asset_header,
    ins={
        "env": AssetIn(
            AssetKey([KEY, "env"]),
        ),
        "script_init_zou": AssetIn(
            AssetKey([KEY, "script_init_zou"]),
        ),
        "build": AssetIn(
            AssetKey([KEY, "build_docker_image"]),
        ),
    },
    deps=[
        AssetKey([KEY, "prepare_db"]),
    ],
)
def compose(
    context: AssetExecutionContext,
    env: dict,  # pylint: disable=redefined-outer-name
    script_init_zou: dict,  # pylint: disable=redefined-outer-name
    build: str,  # pylint: disable=redefined-outer-name
) -> Generator[Output[dict] | AssetMaterialization, None, None]:
    """ """

    # INIT_ZOU.SH
    script_init_zou_path = pathlib.Path(
        env.get("KITSU_INIT_ZOU"),
    )

    script_init_zou_path.parent.mkdir(parents=True, exist_ok=True)

    with open(
        file=script_init_zou_path,
        mode="w",
    ) as sh_init_zou:
        sh_init_zou.write(script_init_zou["script"])

    # # INIT_AND_START_ZOU.SH
    # script_init_and_start_zou = pathlib.Path(
    #     env.get('KITSU_INIT_AND_START_ZOU'),
    # )
    #
    # script_init_and_start_zou.parent.mkdir(parents=True, exist_ok=True)
    #
    # with open(
    #     file=script_init_and_start_zou,
    #     mode="w",
    # ) as sh_init_and_start_zou:
    #     sh_init_and_start_zou.write("#!/bin/bash\n")
    #     sh_init_and_start_zou.write("export LC_ALL=C.UTF-8\n")
    #     sh_init_and_start_zou.write("export LANG=C.UTF-8\n")
    #     sh_init_and_start_zou.write("\n")
    #     sh_init_and_start_zou.write("if [ -z \"$( ls -A '/var/lib/postgresql/14/main' )\" ]; then\n")
    #     sh_init_and_start_zou.write("\tbash /opt/zou/init_zou.sh\n")
    #     sh_init_and_start_zou.write("\techo \"Kitsu DB initialized successfully\"\n")
    #     sh_init_and_start_zou.write("fi\n")
    #     sh_init_and_start_zou.write("\n")
    #     sh_init_and_start_zou.write("bash /opt/zou/start_zou.sh\n")
    #     # sh_init_and_start_zou.write("\n")
    #     # sh_init_and_start_zou.write("echo Success\n")
    #     sh_init_and_start_zou.write("\n")
    #     sh_init_and_start_zou.write("exit 0\n")

    # compile_cmds(
    #     docker_file=build_kitsu,
    #     tag=
    # )

    cmd_docker_run = [
        shutil.which("docker"),
        "run",
        "--rm",
        "--interactive",
        "--tty",
        build,
        "/bin/bash",
    ]

    volumes = [
        f"{env.get('NFS_ENTRY_POINT')}:{env.get('NFS_ENTRY_POINT')}",
        f"{env.get('NFS_ENTRY_POINT')}:{env.get('NFS_ENTRY_POINT_LNS')}",
        # f"{env.get('KITSU_INIT_AND_START_ZOU')}:/opt/zou/init_and_start_zou.sh",
        f"{env.get('KITSU_INIT_ZOU')}:/opt/zou/init_zou.sh",
    ]

    if not KITSUDB_INSIDE_CONTAINER:

        kitsu_db_dir_host = (
            pathlib.Path(env.get("KITSU_DATABASE_INSTALL_DESTINATION"))
            / "postgresql"
            / "14"
            / "main"
        )

        volumes.insert(
            0,
            f"{kitsu_db_dir_host.as_posix()}:/var/lib/postgresql/14/main",
        )

        kitsu_previews_host = (
            pathlib.Path(env.get("KITSU_DATABASE_INSTALL_DESTINATION")) / "previews"
        )
        kitsu_previews_host.mkdir(parents=True, exist_ok=True)

        volumes.insert(
            1,
            f"{kitsu_previews_host}:/opt/zou/previews",
        )

    docker_dict = {
        "services": {
            "kitsu": {
                "container_name": "kitsu",
                "hostname": "kitsu",
                "domainname": env.get("ROOT_DOMAIN"),
                "restart": "always",
                "image": build,
                "volumes": volumes,
                # "healthcheck": {
                #     # Todo:
                #     #  - [ ] fix: test succeeds even if Postgres is down
                #     #  "test": ["CMD-SHELL", "psql -U ${DB_USER} -d ${DB_MAIN} -c 'SELECT 1' || exit 1"],
                #     "test": ["CMD", "curl", "-f", f"http://localhost:{env.get('KITSU_PORT_CONTAINER')}"],
                #     "interval": "10s",
                #     "timeout": "2s",
                #     "retries": "3",
                # },
                "command": [
                    "bash",
                    "/opt/zou/start_zou.sh",
                ],
                "ports": [
                    f"{env.get('KITSU_PORT_HOST')}:{env.get('KITSU_PORT_CONTAINER')}",
                ],
            },
        },
    }

    docker_yaml = yaml.dump(docker_dict)

    yield Output(docker_dict)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
            "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            "cmd_docker_run": MetadataValue.path(cmd_list_to_str(cmd_docker_run)),
        },
    )


group_out = AssetsDefinition.from_op(
    op_group_out,
    group_name=GROUP,
    tags_by_output_name={
        "group_out": {
            "group_out": "third_party",
        },
    },
    key_prefix=KEY,
    keys_by_input_name={
        "compose": AssetKey(
            [KEY, "compose"]
        ),
        "env": AssetKey(
            [KEY, "env"]
        ),
    },
)


docker_compose_graph = AssetsDefinition.from_op(
    op_docker_compose_graph,
    group_name=GROUP,
    key_prefix=KEY,
    keys_by_input_name={
        "group_out": AssetKey(
            [KEY, "group_out"]
        ),
    },
)
