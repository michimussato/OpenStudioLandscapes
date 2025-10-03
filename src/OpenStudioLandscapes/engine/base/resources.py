import base64
import multiprocessing
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
from OpenStudioLandscapes.engine.base import resources
p = resources.run_command(resources.HarborResource.cmd_harbor_up(), sudo=True)
resources.HarborResource().health().json()
# nox -s harbor_down
"""


def run_command(
        command: List[str],
        sudo: bool = False,
        **kwargs,
) -> subprocess.Popen:

    if sudo:
        # https://pexpect.readthedocs.io/en/stable/
        command = [
            # https://gist.github.com/aeroaks/f6150bd0add14bdbc244?permalink_comment_id=4686799#gistcomment-4686799
            "echo",
            "mysudopass",
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
        # env=,
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


    # proc: multiprocessing.Process = multiprocessing.Process()


# https://release-1-9-13.archive.dagster-docs.io/guides/build/external-resources/
class HarborResource(ConfigurableResource):
    username: str = "admin"
    password: str = "Harbor12345"
    project_name: str = "openstudiolandscapes"

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    #     self.proc: multiprocessing.Process = multiprocessing.Process()

    @classmethod
    def docker_progress(cls) -> List:
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

    @classmethod
    def _cmd_harbor(cls) -> List:
        return [
            shutil.which("docker"),
            "compose",
            "--progress",
            HarborResource().docker_progress()[2],
            "--file",
            HarborResource().compose_harbor().as_posix(),
            "--project-name",
            "openstudiolandscapes-harbor",
        ]

    @classmethod
    def _cmd_harbor_up(
            cls,
            detach: bool,
    ) -> List[str]:
        cmd = [
            *HarborResource()._cmd_harbor(),
            "up",
            "--remove-orphans",
        ]

        if detach:
            cmd.append("--detach")

        return cmd

    cmd_harbor_up = partialmethod(_cmd_harbor_up, detach=False)
    cmd_harbor_up_detach = partialmethod(_cmd_harbor_up, detach=True)

    @classmethod
    def cmd_harbor_down(cls) -> List[str]:
        cmd = [
            *HarborResource().cmd_harbor(),
            "down",
        ]

        return cmd

    @property
    def _authorization(self) -> str:
        return f"{base64.b64encode(str(':'.join([self.username, self.password])).encode('utf-8')).decode('ascii')}"

    harbor_url: str = EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_URL").get_value() or "http://localhost:80"
    endpoint_api: str = f"{harbor_url}/api/v2.0"

    @classmethod
    def _ping(cls) -> Dict:
        _ping_: dict = {
            "endpoint": f"{HarborResource().endpoint_api}/ping",
            "method": requests.get,
            "headers": {
                "accept": "text/plain",
            },
        }
        return _ping_

    @classmethod
    def _health(cls) -> Dict:
        _health_: dict = {
            "endpoint": f"{HarborResource().endpoint_api}/health",
            "method": requests.get,
            "headers": {
                "accept": "application/json",
            },
        }
        return _health_

    @classmethod
    def _systeminfo(cls) -> Dict:
        _systeminfo_: dict = {
            "endpoint": f"{HarborResource().endpoint_api}/systeminfo",
            "method": requests.get,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {HarborResource()._authorization}",
            },
        }
        return _systeminfo_

    @classmethod
    def _systeminfo_volumes(cls) -> Dict:
        _systeminfo_volumes_: dict = {
            "endpoint": f"{HarborResource().systeminfo['endpoint']}/volumes",
            "method": requests.get,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {HarborResource()._authorization}",
            },
        }
        return _systeminfo_volumes_

    @classmethod
    def _projects_head(cls) -> Dict:
        _projects_head_: dict = {
            "endpoint": f"{HarborResource().endpoint_api}/projects",
            "method": requests.head,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {HarborResource()._authorization}",
            },
        }
        return _projects_head_

    @classmethod
    def _projects_create(cls) -> Dict:
        _projects_create_: dict = {
            "endpoint": f"{HarborResource().projects_head['endpoint']}",
            "method": requests.post,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {HarborResource()._authorization}",
                "X-Resource-Name-In-Location": "false",
                "Content-Type": "application/json",
            },
        }
        return _projects_create_

    @classmethod
    def _projects_delete(cls) -> Dict:
        _projects_delete_: dict = {
            "endpoint": f"{HarborResource().projects_head['endpoint']}",
            "method": requests.delete,
            "headers": {
                "accept": "application/json",
                "authorization": f"Basic {HarborResource()._authorization}",
                "X-Is-Resource-Name": "false"
            },
        }
        return _projects_delete_

    def delete_project(self, project_name) -> requests.Response:

        project_exists = self.query_project_exists(
            project_name=project_name,
        )

        if project_exists.status_code == requests.codes.ok:
            response = self._projects_delete()["method"](
                url=f"{self._projects_delete()['endpoint']}/{project_name}",
                headers=self._projects_delete()["headers"]
            )
            return response

        else:
            return project_exists

    delete_library = partialmethod(delete_project, project_name="library")

    @classmethod
    def health(
        cls,
    ) -> requests.Response:

        response = cls._health()["method"](
            url=cls._health()["endpoint"],
            headers=cls._health()["headers"],
        )

        return response

    @classmethod
    def ping(
        cls,
    ) -> requests.Response:

        response = cls._ping()["method"](
            url=cls._ping()["endpoint"],
            headers=cls._ping()["headers"],
        )

        return response

    @classmethod
    def query_project_exists(
        cls,
        project_name: str,
    ) -> requests.Response:

        response = cls._projects_head()["method"](
            url=f"{cls._projects_head()['endpoint']}?project_name={project_name}",
            headers=cls._projects_head()["headers"],
        )

        return response

    def create_project(self) -> requests.Response:

        project_exists = self.query_project_exists(
            project_name=self.project_name,
        )

        if not project_exists.status_code == requests.codes.ok:
            response = self.projects_create["method"](
                url=self.projects_create["endpoint"],
                headers=self.projects_create["headers"],
                json={
                    "project_name": self.project_name,
                    "public": True,
                },
            )
            return response
        else:
            return project_exists

    def harbor_prepare(self) -> Exception:
        raise NotImplementedError("This is not implemented yet")

    def harbor_up(self) -> Exception:
        raise NotImplementedError("This is not implemented yet")

    def harbor_init(self) -> Exception:
        raise NotImplementedError("This is not implemented yet")

    def harbor_down(self) -> Exception:
        raise NotImplementedError("This is not implemented yet")


resources = {
    "harbor_resource": HarborResource(
        username=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_USERNAME"),
        password=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD"),
    )
}
