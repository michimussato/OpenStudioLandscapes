import base64
import json
import multiprocessing
import os
import pathlib
import shutil
import subprocess
import tarfile
from functools import partialmethod

import yaml
from typing import Dict, List

import requests
from dagster import (
    ConfigurableResource,
    EnvVar,
    get_dagster_logger,
    ResourceDependency,
    AssetExecutionContext
)

LOGGER = get_dagster_logger(__name__)


# Fork vs. Spawn
# https://www.geeksforgeeks.org/operating-systems/understanding-fork-and-spawn-in-python-multiprocessing/
try:
    multiprocessing.set_start_method(
        [
            "fork",
            "spawn",
        ][1]
    )
except RuntimeError:
    pass


"""
import os
os.environ["OPENSTUDIOLANDSCAPES__HARBOR_USERNAME"] = "admin"
os.environ["OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD"] = "Harbor12345"
os.environ["OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR"] = "/home/michael/git/repos/OpenStudioLandscapes/.harbor"
os.environ["OPENSTUDIOLANDSCAPES__HARBOR_BIN_DIR"] = "bin"
os.environ["OPENSTUDIOLANDSCAPES__HARBOR_DOWNLOAD_DIR"] = "download"
os.environ["OPENSTUDIOLANDSCAPES__HARBOR_DATA_DIR"] = "data"

from OpenStudioLandscapes.engine.base import resources
r = resources.HarborResource()
returncode = r.harbor_up()




r.health().json()
r.query_project_exists("library")
r.create_project("hello_world")
r.list_projects().json()
r.delete_project("hello_world")
pd = r.harbor_down()
with pu.stdout:
    for l in iter(pu.stdout.readline, b""):
        print(l)
"""

"""
s = r.shell()
ls = "ls -al".encode("utf-8")
output, _ = s.communicate(input=ls)
print(output.decode("utf-8"))
"""


def get_full_command(
        command: List[str],
        sudo: bool = False,
        **kwargs,
) -> List[str]:

    if sudo:

        command = [
            # https://gist.github.com/aeroaks/f6150bd0add14bdbc244?permalink_comment_id=4686799#gistcomment-4686799
            # https://www.cyberciti.biz/open-source/command-line-hacks/linux-run-command-as-different-user/
            shutil.which("pkexec"),
            # To unlock a user after failed login attempt
            # - "X minutes left to unlock"
            # https://wiki.archlinux.org/title/Security#Lock_out_user_after_three_failed_login_attempts
        ] + command

    return command


def run_command(
        command: List[str],
        **kwargs,
) -> subprocess.Popen:

    LOGGER.info("Starting Harbor...")
    LOGGER.debug(f"{command = }")

    print(f"{command = }")
    # print(f"{' '.join(command) = }")

    process = subprocess.Popen(
        " ".join(command),
        # cwd=,
        # env={
        #     "SUDO_PASS": os.environ.get("SUDO_PASS"),
        # },
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.PIPE,
        start_new_session=True,
        shell=True,
        text=True,
        # bufsize=1,
        **kwargs,
    )

    return process


class PiholeResource(ConfigurableResource):
    pass


class TeleportResource(ConfigurableResource):
    pass


# Resource State
# https://release-1-9-13.archive.dagster-docs.io/guides/build/external-resources/managing-resource-state


# https://coderivers.org/blog/python-subprocess-popen/
class Pipe:
    proc = None


# https://release-1-9-13.archive.dagster-docs.io/guides/build/external-resources/
class HarborResource(ConfigurableResource):

    # _username: str = PrivateAttr()
    username: str = "admin"
    # _password: str = PrivateAttr()
    password: str = "Harbor12345"

    root_dir: ResourceDependency[pathlib.Path] = pathlib.Path("/home/michael/git/repos/OpenStudioLandscapes/.harbor")
    bin_dir: ResourceDependency[str] = "bin"
    download_dir: ResourceDependency[str] = "download"
    data_dir: ResourceDependency[str] = "data"

    pipe: ResourceDependency[object] = Pipe

    @property
    def proc(self):
        return self.pipe.proc

    @proc.setter
    def proc(self, value):
        self.pipe.proc = value

    @property
    def project_name(self):
        return "openstudiolandscapes"

    @property
    def docker_progress(self) -> List:
        return [
            "auto",
            "quiet",
            "plain",
            "tty",
            "rawjson",
        ]

    @property
    def compose_harbor(self) -> pathlib.Path:
        return self.root_dir / self.bin_dir / "docker-compose.yml"

    # COMMAND BLUE PRINTS
    @property
    def _cmd_harbor(self) -> List:
        return [
            shutil.which("docker"),
            "compose",
            "--progress",
            self.docker_progress[2],
            "--file",
            self.compose_harbor.as_posix(),
            "--project-name",
            "openstudiolandscapes-harbor",
        ]

    def _cmd_harbor_up(
            self,
            detach: bool,
    ) -> List[str]:
        cmd = [
            *self._cmd_harbor,
            "up",
            "--remove-orphans",
        ]

        if detach:
            cmd.append("--detach")

        return cmd

    def _cmd_harbor_restart(self) -> List[str]:
        cmd = [
            *self._cmd_harbor,
            "restart",
        ]

        return cmd

    def _cmd_harbor_down(self) -> List[str]:
        cmd = [
            *self._cmd_harbor,
            "down",
        ]

        return cmd

    # COMMANDS
    @property
    def cmd_harbor_up(self) -> List[str]:
        return get_full_command(
            command=self._cmd_harbor_up(detach=False),
            sudo=True,
        )

    @property
    def cmd_harbor_restart(self) -> List[str]:
        return get_full_command(
            command=self._cmd_harbor_restart(),
            sudo=True,
        )

    @property
    def cmd_harbor_up_detached(self) -> List[str]:
        return get_full_command(
            command=self._cmd_harbor_up(detach=True),
            sudo=True,
        )

    @property
    def cmd_harbor_down(self) -> List[str]:
        cmd = [
            *self._cmd_harbor_down(),
        ]

        return get_full_command(
            command=cmd,
            sudo=True,
        )

    @property
    def cmd_harbor_ps(self) -> List[str]:
        """
        Docker Documentation:
        https://docs.docker.com/reference/cli/docker/compose/ps/
        """
        cmd = [
            *self._cmd_harbor,
            "ps",
            "--format=json",
        ]

        return cmd

    @property
    def _authorization(self) -> str:
        return f"{base64.b64encode(str(':'.join([self.username, self.password])).encode('utf-8')).decode('ascii')}"

    harbor_url: str = EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_URL").get_value() or "http://localhost:80"
    endpoint_api: str = f"{harbor_url}/api/v2.0"

    # API ACCESS BLUE PRINTS
    @property
    def _ping(self) -> Dict:
        _ping_: dict = {
            "endpoint": f"{self.endpoint_api}/ping",
            "method": requests.get,
            "headers": {
                "accept": "text/plain",
            },
        }
        return _ping_

    @property
    def _health(self) -> Dict:
        _health_: dict = {
            "endpoint": f"{self.endpoint_api}/health",
            "method": requests.get,
            "headers": {
                "accept": "application/json",
            },
        }
        return _health_

    @property
    def _systeminfo(self) -> Dict:
        _systeminfo_: dict = {
            "endpoint": f"{self.endpoint_api}/systeminfo",
            "method": requests.get,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {self._authorization}",
            },
        }
        return _systeminfo_

    @property
    def _systeminfo_volumes(self) -> Dict:
        _systeminfo_volumes_: dict = {
            "endpoint": f"{self._systeminfo['endpoint']}/volumes",
            "method": requests.get,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {self._authorization}",
            },
        }
        return _systeminfo_volumes_

    @property
    def _projects_list(self) -> Dict:
        _projects_head_: dict = {
            "endpoint": f"{self.endpoint_api}/projects?with_detail=true",
            "method": requests.get,
            "headers": {
                "accept": "application/json",
            },
        }
        return _projects_head_

    @property
    def _projects_head(self) -> Dict:
        _projects_head_: dict = {
            "endpoint": f"{self.endpoint_api}/projects",
            "method": requests.head,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {self._authorization}",
            },
        }
        return _projects_head_

    @property
    def _projects_create(self) -> Dict:
        _projects_create_: dict = {
            "endpoint": f"{self._projects_head['endpoint']}",
            "method": requests.post,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {self._authorization}",
                "X-Resource-Name-In-Location": "false",
                "Content-Type": "application/json",
            },
        }
        return _projects_create_

    @property
    def _projects_delete(self) -> Dict:
        _projects_delete_: dict = {
            "endpoint": f"{self._projects_head['endpoint']}",
            "method": requests.delete,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {self._authorization}",
                "X-Is-Resource-Name": "false"
            },
        }
        return _projects_delete_

    # API ACCESS
    def delete_project(self, project_name) -> requests.Response:

        project_exists = self.query_project_exists(
            project_name=project_name,
        )

        if project_exists.status_code == requests.codes.ok:
            response = self._projects_delete["method"](
                url=f"{self._projects_delete['endpoint']}/{project_name}",
                headers=self._projects_delete["headers"]
            )
            return response

        else:
            return project_exists

    def systeminfo(self) -> requests.Response:

        response = self._systeminfo["method"](
            url=self._systeminfo["endpoint"],
            headers=self._systeminfo["headers"],
        )

        return response

    def systeminfo_volumes(self) -> requests.Response:

        response = self._systeminfo_volumes["method"](
            url=self._systeminfo_volumes["endpoint"],
            headers=self._systeminfo_volumes["headers"],
        )

        return response

    delete_library = partialmethod(delete_project, project_name="library")

    def health(
        self,
    ) -> requests.Response:

        response = self._health["method"](
            url=self._health["endpoint"],
            headers=self._health["headers"],
        )

        return response

    def ping(
        self,
    ) -> requests.Response:

        response = self._ping["method"](
            url=self._ping["endpoint"],
            headers=self._ping["headers"],
        )

        return response

    def list_projects(
        self,
    ) -> requests.Response:

        response = self._projects_list["method"](
            url=self._projects_list["endpoint"],
            headers=self._projects_list["headers"],
        )

        return response

    def query_project_exists(
        self,
        project_name: str,
    ) -> requests.Response:

        response = self._projects_head["method"](
            url=f"{self._projects_head['endpoint']}?project_name={project_name}",
            headers=self._projects_head["headers"],
        )

        return response

    def create_project(
            self,
            project_name: str,
    ) -> requests.Response:

        project_exists = self.query_project_exists(
            project_name=project_name,
        )

        if not project_exists.status_code == requests.codes.ok:
            response = self._projects_create["method"](
                url=self._projects_create["endpoint"],
                headers=self._projects_create["headers"],
                json={
                    "project_name": project_name,
                    "public": True,
                },
            )
            return response
        else:
            return project_exists

    # HARBOR EXECUTION API
    def harbor_prepare(
            self,
            context: AssetExecutionContext,
    ) -> List:
        sudo = False

        harbor_root_dir: pathlib.Path = pathlib.Path(os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR", "/home/michael/git/repos/OpenStudioLandscapes/.harbor"))
        harbor_root_dir.mkdir(parents=True, exist_ok=True)

        harbor_bin_dir: pathlib.Path = (
                harbor_root_dir / os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_BIN_DIR", "bin")
        )
        harbor_bin_dir.mkdir(parents=True, exist_ok=True)

        prepare: pathlib.Path = harbor_bin_dir / "prepare"

        if prepare.exists():
            context.log.info(
                f"`prepare` already present in {prepare.parent.as_posix()}. Use that or start fresh by "
                "issuing `nox --session harbor_clear` first."
            )
            return []

        harbor_download_dir = harbor_root_dir / os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_DOWNLOAD_DIR", "download")
        harbor_download_dir.mkdir(parents=True, exist_ok=True)

        def download(
            url: str,
            dest_folder: pathlib.Path,
        ) -> pathlib.Path:
            if not dest_folder.exists():
                dest_folder.mkdir(
                    parents=True, exist_ok=True
                )  # create folder if it does not exist

            filename = url.split("/")[-1].replace(" ", "_")  # be careful with file names
            file_path = dest_folder / filename

            r = requests.get(url, stream=True)
            if r.ok:
                context.log.info("Saving to %s" % file_path.absolute().as_posix())
                with open(file_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 8):
                        if chunk:
                            f.write(chunk)
                            f.flush()
                            os.fsync(f.fileno())
                return file_path
            else:  # HTTP status code 4XX/5XX
                raise Exception(
                    "Download failed: status code {}\n{}".format(r.status_code, r.text)
                )

        def setup_harbor(
                harbor_download_dir: pathlib.Path,
        ) -> pathlib.Path:

            file_path: pathlib.Path = download(
                url=f"{os.environ['OPENSTUDIOLANDSCAPES__HARBOR_INSTALLER_ONLINE']}".format(
                    **os.environ,
                ),
                dest_folder=harbor_download_dir,
            )

            context.log.info("File successfully downloaded to %s" % file_path.as_posix())

            return file_path

        tar_file = setup_harbor(
            harbor_download_dir=harbor_download_dir,
        )

        # equivalent to tar --strip-components=1
        # Credits: https://stackoverflow.com/a/78461535
        strip1 = lambda member, path: member.replace(
            name=pathlib.Path(*pathlib.Path(member.path).parts[1:])
        )

        context.log.debug("Extracting tar file...")
        with tarfile.open(tar_file, "r:gz") as tar:
            tar.extractall(
                path=harbor_bin_dir,
                filter=strip1,
            )
        context.log.debug("All files extracted to %s" % harbor_bin_dir.as_posix())

        def write_harbor_yml(
                yaml_out: pathlib.Path,
        ) -> pathlib.Path:

            harbor_root_dir: pathlib.Path = pathlib.Path(os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR", "/home/michael/git/repos/OpenStudioLandscapes/.harbor"))
            harbor_root_dir.mkdir(parents=True, exist_ok=True)

            harbor_data_dir = harbor_root_dir / os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_DATA_DIR", "data")
            harbor_data_dir.mkdir(parents=True, exist_ok=True)

            harbor_dict = {
                "hostname": os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME", "harbor.farm.evil"),
                "http": {"port": os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAMEOPENSTUDIOLANDSCAPES__HARBOR_PORT", "80")},
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

            context.log.debug(
                "Harbor Configuration = %s"
                % json.dumps(
                    obj=harbor_dict,
                    sort_keys=True,
                    indent=2,
                )
            )

            harbor_yml: str = yaml.dump(
                harbor_dict,
                indent=2,
            )

            with open(yaml_out, "w") as fw:
                fw.write(harbor_yml)

            context.log.debug("Contents harbor.yml: \n%s" % harbor_yml)

            return yaml_out

        harbor_yml: pathlib.Path = write_harbor_yml(
            yaml_out=harbor_bin_dir / "harbor.yml",
        )

        if not harbor_yml.exists():
            raise FileNotFoundError("`harbor.yml` file not found. Not able to continue.")

        prepare: pathlib.Path = harbor_bin_dir / "prepare"

        if not prepare.exists():
            raise FileNotFoundError("`prepare` file not found. " "Not able to continue.")

        context.log.debug("Preparing Harbor...")

        cmd = [
            shutil.which("bash"),
            prepare.as_posix(),
        ]

        if sudo:
            cmd.insert(0, shutil.which("sudo"))
            cmd.insert(1, "--reset-timestamp")
            # cmd.insert(2, "--stdin")

        context.log.info(f"{cmd = }")

        return cmd

    def harbor_up(self, detached=True) -> int:
        if detached:
            cmd = self.cmd_harbor_up_detached
        else:
            cmd = self.cmd_harbor_up

        if self.proc is None:
            self.pipe.proc = run_command(cmd)
            if detached:
                self.pipe.proc.wait()
        elif not detached and self.proc.poll() is None:
            # if detached is True, polling doesn't work in a useful way.
            # need some other mechanism to verify whether Harbor is running or not.
            raise Exception(f"Harbor is already running.")

        return self.pipe.proc.returncode

    def harbor_restart(self) -> int:
        """
        It might be a bit crippled but for now I don't have a
        good idea how to leverage `docker compose restart`
        without loosing track of the self.pipe.proc object.
        So, for now: `docker compose down` and `docker compose up`.
        """
        if not self.harbor_down():
            ret = self.harbor_up(detached=True)

        return ret

    def harbor_init(self) -> Exception:
        raise NotImplementedError("This is not implemented yet")

    def harbor_down(self) -> int:

        if self.proc is None \
                or self.proc.poll() is None:
            raise Exception("Harbor is not running.")

        self.pipe.proc = run_command(self.cmd_harbor_down)
        self.pipe.proc.wait()
        ret = self.pipe.proc.returncode

        if bool(ret):
            raise Exception(f"Unable to stop Harbor.")

        self.pipe.proc = None

        return ret

    def systemd_unit_dict(
            self,
            context: AssetExecutionContext,
    ) -> Dict:
        # /usr/bin/pkexec /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.harbor/bin/docker-compose.yml --project-name openstudiolandscapes-harbor up --remove-orphans --detach

        # unit = configparser.ConfigParser()
        # # Change from case insensitive to case sensitive
        # # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.optionxform
        # unit.optionxform = str

        unit_dict = {
            "Unit": {
                "Description": "Harbor",
                "Documentation": "https://goharbor.io/",
            },
            "Service": {
                "Type": "simple",
                "User": "root",
                "Group": "root",
                "Restart": "always",
                "WorkingDirectory": self.compose_harbor.parent.as_posix(),
                "ExecStart": " ".join(self._cmd_harbor_up(detach=False)),
                "ExecReload": " ".join(self._cmd_harbor_restart()),
                "ExecStop": " ".join(self._cmd_harbor_down()),
            },
            "Install": {
                "WantedBy": "multi-user.target",
            },
        }

        context.log.warning(unit_dict)

        return unit_dict


resources = {
    "harbor_resource": HarborResource(
        username=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_USERNAME"),
        password=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD"),
        root_dir=pathlib.Path(os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR", "/home/michael/git/repos/OpenStudioLandscapes/.harbor")),
        bin_dir=os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_BIN_DIR", "bin"),
        download_dir=os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_DOWNLOAD_DIR", "download"),
        data_dir=os.environ.get("OPENSTUDIOLANDSCAPES__HARBOR_DATA_DIR", "data"),
    ),
    # "harbor_popen" : HarborResource,
}
