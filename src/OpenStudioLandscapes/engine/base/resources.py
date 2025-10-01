import base64
from typing import Dict

import requests
from dagster import ConfigurableResource, EnvVar, get_dagster_logger

LOGGER = get_dagster_logger(__name__)


# https://release-1-9-13.archive.dagster-docs.io/guides/build/external-resources/
class HarborResource(ConfigurableResource):
    username: str = "admin"
    password: str = "Harbor12345"
    harbor_url: str
    project_name: str = "openstudiolandscapes"

    @property
    def _authorization(self) -> str:
        return f"{base64.b64encode(str(':'.join([self.username, self.password])).encode('utf-8')).decode('ascii')}"

    @property
    def headers(self) -> Dict[str, str]:
        ret = {
            "accept": "application/json",
            "authorization": f"Basic {self._authorization}",
        }
        return ret

    @property
    def endpoint_projects(self) -> str:
        return f"{self.harbor_url}/api/v2.0/projects"

    def delete_library(self) -> requests.Response:

        library_exists = self.query_project_exists(
            project_name="library",
        )

        if library_exists.status_code == requests.codes.ok:

            response = requests.delete(
                url=f"{self.endpoint_projects}/library",
                headers={
                    **self.headers,
                    "X-Is-Resource-Name": "false",
                },
            )
            return response

        else:
            return library_exists

    def query_project_exists(
        self,
        project_name: str,
    ) -> requests.Response:
        response = requests.head(
            url=f"{self.endpoint_projects}?project_name={project_name}",
            headers={
                **self.headers,
            },
        )
        return response

    def create_project(self) -> requests.Response:

        project_exists = self.query_project_exists(
            project_name=self.project_name,
        )

        if not project_exists.status_code == requests.codes.ok:
            response = requests.post(
                url=f"{self.endpoint_projects}",
                headers={
                    **self.headers,
                    "X-Resource-Name-In-Location": "false",
                    "Content-Type": "application/json",
                },
                json={
                    "project_name": self.project_name,
                    "public": True,
                },
            )
            return response
        else:
            return project_exists

    def harbor_prepare(self) -> NotImplementedError:
        raise NotImplementedError("This is not implemented yet")

    def harbor_up(self) -> NotImplementedError:
        raise NotImplementedError("This is not implemented yet")

    def harbor_init(self) -> NotImplementedError:
        raise NotImplementedError("This is not implemented yet")

    def harbor_down(self) -> NotImplementedError:
        raise NotImplementedError("This is not implemented yet")


resources = {
    "harbor_resource": HarborResource(
        username=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_USERNAME"),
        password=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD"),
        harbor_url=EnvVar("OPENSTUDIOLANDSCAPES__HARBOR_URL"),
    )
}
