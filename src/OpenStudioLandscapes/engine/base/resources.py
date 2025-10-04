import base64
import multiprocessing
import os
import pathlib
import shutil
import subprocess
from functools import partialmethod
from pydantic import PrivateAttr
from typing import Dict, List

import requests
from dagster import (
    ConfigurableResource, EnvVar, get_dagster_logger, Config, ResourceDependency, InitResourceContext
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


# def run_command(
#         command: List[str],
#         sudo: bool = False,
#         **kwargs,
# ) -> subprocess.Popen:
#
#     if sudo:
#
#         assert "SUDO_PASS" in os.environ
#         # https://pexpect.readthedocs.io/en/stable/
#         command = [
#             # https://gist.github.com/aeroaks/f6150bd0add14bdbc244?permalink_comment_id=4686799#gistcomment-4686799
#             "echo",
#             "${SUDO_PASS}",
#             "|",
#             shutil.which("sudo"),
#             "-S",
#             "--reset-timestamp",
#         ] + command
#
#     LOGGER.info("Starting Harbor...")
#     LOGGER.debug(f"{command = }")
#
#     process = subprocess.Popen(
#         " ".join(command),
#         # cwd=,
#         env={
#             "SUDO_PASS": os.environ.get("SUDO_PASS"),
#         },
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         start_new_session=True,
#         shell=True,
#         **kwargs,
#     )
#
#     return process


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


# class HarborPool:
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)
#
#         self.pool = multiprocessing.Pool(*args, **kwargs)


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
            *self._cmd_harbor,
            "down",
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

    def harbor_prepare(self) -> Exception:
        raise NotImplementedError("This is not implemented yet")

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
