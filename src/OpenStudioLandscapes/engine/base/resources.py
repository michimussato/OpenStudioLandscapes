import base64
import multiprocessing
import os
import pathlib
# import pexpect
import shutil
import subprocess
from functools import partialmethod
from typing import Dict, List

import requests
from dagster import (
    ConfigurableResource, EnvVar, get_dagster_logger
)

LOGGER = get_dagster_logger(__name__)


# Fork vs. Spawn
# https://www.geeksforgeeks.org/operating-systems/understanding-fork-and-spawn-in-python-multiprocessing/
multiprocessing.set_start_method(
    [
        "fork",
        "spawn",
    ][1]
)


"""
import os
os.environ["SUDO_PASS"] = ""
from OpenStudioLandscapes.engine.base import resources
r = resources.HarborResource()
pu = r.harbor_up()
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


def run_command(
        command: List[str],
        sudo: bool = False,
        **kwargs,
) -> subprocess.Popen:

    if sudo:

        assert "SUDO_PASS" in os.environ
        # https://pexpect.readthedocs.io/en/stable/
        command = [
            # https://gist.github.com/aeroaks/f6150bd0add14bdbc244?permalink_comment_id=4686799#gistcomment-4686799
            "echo",
            "${SUDO_PASS}",
            "|",
            shutil.which("sudo"),
            "-S",
            "--reset-timestamp",
        ] + command

    LOGGER.info("Starting Harbor...")
    LOGGER.debug(f"{command = }")

    process = subprocess.Popen(
        " ".join(command),
        # cwd=,
        env={
            "SUDO_PASS": os.environ.get("SUDO_PASS"),
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=True,
        shell=True,
        **kwargs,
    )

    return process


class PiholeResource(ConfigurableResource):
    pass


class TeleportResource(ConfigurableResource):
    pass


# Resource State
# https://release-1-9-13.archive.dagster-docs.io/guides/build/external-resources/managing-resource-state


class HarborPool:
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)

        self.pool = multiprocessing.Pool(*args, **kwargs)



# https://release-1-9-13.archive.dagster-docs.io/guides/build/external-resources/
class HarborResource(ConfigurableResource):
    username: str = "admin"
    password: str = "Harbor12345"

    def run_in_pool(self, func, cmd):
        self._pool.pool.map(func, cmd)

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

    # # ENVIRONMENT
    @classmethod
    def environment_harbor(cls) -> Dict:
        return {
            "HARBOR_HOSTNAME": "harbor.farm.evil",
            "HARBOR_ADMIN": "admin",
            "HARBOR_PASSWORD": "Harbor12345",
            # Todo:
            #  - [ ] Try with:
            # "HARBOR_ADMIN": "harbor@openstudiolandscapes.org",
            # "HARBOR_PASSWORD": "0penstudiolandscapes",
            "HARBOR_PORT": "88",  # port 80 is reserved for acme_sh for now
            "HARBOR_RELEASE": [
                "v2.12.2",
                "v2.13.0",
            ][0],
            "HARBOR_INSTALLER": {
                "online": "https://github.com/goharbor/harbor/releases/download/{HARBOR_RELEASE}/harbor-online-installer-{HARBOR_RELEASE}.tgz",
                "offline": "https://github.com/goharbor/harbor/releases/download/{HARBOR_RELEASE}/harbor-offline-installer-{HARBOR_RELEASE}.tgz",
            }["online"],
            "HARBOR_ROOT_DIR": pathlib.Path(pathlib.Path.cwd() / ".harbor").as_posix(),
            "HARBOR_BIN_DIR": "bin",
            "HARBOR_DOWNLOAD_DIR": "download",
            "HARBOR_DATA_DIR": "data",
        }

    @classmethod
    def compose_harbor(cls) -> pathlib.Path:
        return pathlib.Path(
                HarborResource().environment_harbor()["HARBOR_ROOT_DIR"],
                HarborResource().environment_harbor()["HARBOR_BIN_DIR"],
                "docker-compose.yml"
            )

    @property
    def _cmd_harbor(self) -> List:
        return [
            shutil.which("docker"),
            "compose",
            "--progress",
            self.docker_progress[2],
            "--file",
            self.compose_harbor().as_posix(),
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

    @property
    def cmd_harbor_up(self) -> List[str]:
        return self._cmd_harbor_up(detach=False)

    @property
    def cmd_harbor_up_detached(self) -> List[str]:
        return self._cmd_harbor_up(detach=True)

    @property
    def cmd_harbor_down(self) -> List[str]:
        cmd = [
            *self._cmd_harbor,
            "down",
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
            "endpoint": f"{self.systeminfo['endpoint']}/volumes",
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

    def harbor_up(self) -> subprocess.Popen:
        p = run_command(self.cmd_harbor_up, sudo=True)
        return p

    def harbor_init(self) -> Exception:
        raise NotImplementedError("This is not implemented yet")

    def harbor_down(self) -> subprocess.Popen:
        p = run_command(self.cmd_harbor_down, sudo=True)
        return p


resources = {
    "harbor_resource": HarborResource(
        username=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_USERNAME"),
        password=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD")
    )
}
