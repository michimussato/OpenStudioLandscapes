import os
import pathlib
import shlex
import shutil
from typing import Generator

import yaml
from dagster import (
    AssetExecutionContext,
    AssetIn,
    AssetKey,
    AssetMaterialization,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)

from OpenStudioLandscapes.engine.base.ops import op_docker_compose_graph, op_group_out
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *

# Todo:
#  - [ ] Find a procedural way to deal with this
from OpenStudioLandscapes.Deadline_10_2_Worker.constants import KEY as KEY_WORKER


# Dynamic inputs based on the imported
# third party code locations
ins = {}
for i in IMPORTED_FEATURES:
    # ex: module = "OpenStudioLandscapes.Ayon.definitions"
    module = i["module"]
    compose_scope = i["compose_scope"]
    if compose_scope == ComposeScope.WORKER:
        split = module.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))


if bool(ins):
    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "group_in": AssetIn(AssetKey([*KEY_BASE, "group_out"])),
        },
        deps=[
            AssetKey(
                [
                    *ASSET_HEADER_COMPOSE_WORKER["key_prefix"],
                    "constants_compose_worker",
                ]
            )
        ],
    )
    def env(
        context: AssetExecutionContext,
        group_in: dict,
    ) -> Generator[Output[dict] | AssetMaterialization, None, None]:

        ret = group_in.get("env", {})

        ret.update(
            {
                "COMPOSE_SCOPE": ComposeScope.WORKER,
            }
        )

        yield Output(ret)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(ret),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "env": AssetIn(
                AssetKey([*KEY_COMPOSE_WORKER, "env"]),
            ),
            **ins,
        },
    )
    def compose(
        context: AssetExecutionContext,
        env: dict,  # pylint: disable=redefined-outer-name
        **kwargs,
    ) -> Generator[
        Output[dict[str, list[dict[str, list]]]] | AssetMaterialization, None, None
    ]:
        """ """

        context.log.info(kwargs)

        _group_in = []

        docker_compose = pathlib.PurePosixPath(
            env["DOT_LANDSCAPES"],
            env.get("LANDSCAPE", "default"),
            f"{GROUP_COMPOSE_WORKER}__{'__'.join(KEY_COMPOSE_WORKER)}",
            "__".join(context.asset_key.path),
            "docker_compose",
            "docker-compose.yml",
        )

        context.log.info(docker_compose)
        context.log.info(type(docker_compose))

        for v in kwargs.values():
            _rel_path = os.path.relpath(
                path=v.as_posix(),
                start=docker_compose.parent.as_posix(),
            )
            rel_path = pathlib.Path(_rel_path)

            _group_in.append(rel_path)

        docker_dict = {
            "include": [{"path": [i.as_posix()]} for i in _group_in],
        }

        docker_yaml = yaml.dump(docker_dict)

        yield Output(docker_dict)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(docker_dict),
                "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml}\n```"),
            },
        )


    # Todo:
    #  - [ ] This is a bit hacky. Maybe there is a better way
    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "env": AssetIn(
                AssetKey([*KEY_COMPOSE_WORKER, "env"]),
            ),
            "cmd_docker_compose_up_dict": AssetIn(
                AssetKey([*KEY_COMPOSE_WORKER, "cmd_docker_compose_up"]),
            ),
            "compose_pulse_runner": AssetIn(
                AssetKey([*KEY_WORKER, "compose_pulse_runner"]),
            ),
            "compose_worker_runner": AssetIn(
                AssetKey([*KEY_WORKER, "compose_worker_runner"]),
            ),
        },
    )
    def compose_up_and_hostname(
            context: AssetExecutionContext,
            env: dict,  # pylint: disable=redefined-outer-name
            cmd_docker_compose_up_dict: dict[str, list],  # pylint: disable=redefined-outer-name,
            compose_pulse_runner: dict,  # pylint: disable=redefined-outer-name,
            compose_worker_runner: dict,  # pylint: disable=redefined-outer-name,
    ):

        # Todo:
        #  - [x] for i in range(NUM_SERVICES): [...]

        compose_pulse_runner_services = list(compose_pulse_runner["services"].keys())
        compose_worker_runner_services = list(compose_worker_runner["services"].keys())

        # Example cmd:
        # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --detach --remove-orphans && sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname -f)-nice-hack"

        cmd_docker_compose_up = cmd_docker_compose_up_dict["cmd_docker_compose_up"]
        # cmd_docker_compose_pull_up = cmd_docker_compose_up_dict["cmd_docker_compose_pull_up"]
        # cmd_docker_compose_down = cmd_docker_compose_up_dict["cmd_docker_compose_down"]
        cmd_docker_compose_logs = cmd_docker_compose_up_dict["cmd_docker_compose_logs"]

        context.log.info(cmd_docker_compose_up)

        cmd_docker_compose_up.extend(
            [
                # needs to be detached in order to get to do sudo
                "--detach",
            ]
        )

        exclude_from_quote = []

        cmd_docker_compose_set_dynamic_hostnames = []

        # Transform container hostnames
        # - deadline-10-2-worker-001...nnn
        # - deadline-10-2-pulse-worker-001...nnn
        # into
        # - $(hostname)-deadline-10-2-worker-001...nnn
        # - $(hostname)-deadline-10-2-pulse-worker-001...nnn
        for service_name in zip(
                compose_worker_runner_services,
                compose_pulse_runner_services,
        ):

            target_worker = "$(docker inspect -f '{{ .State.Pid }}' %s)" % "--".join([service_name[0], env.get("LANDSCAPE", "default")])
            target_pulse = "$(docker inspect -f '{{ .State.Pid }}' %s)" % "--".join([service_name[1], env.get("LANDSCAPE", "default")])
            hostname_worker = f"$(hostname)-{service_name[0]}"
            hostname_pulse = f"$(hostname)-{service_name[1]}"

            exclude_from_quote.extend(
                [
                    target_worker,
                    target_pulse,
                    hostname_worker,
                    hostname_pulse
                ]
            )

            cmd_docker_compose_set_dynamic_hostname_worker = [
                shutil.which("sudo"),
                shutil.which("nsenter"),
                "--target", target_worker,
                "--uts",
                "hostname",
                hostname_worker,
            ]

            cmd_docker_compose_set_dynamic_hostname_pulse = [
                shutil.which("sudo"),
                shutil.which("nsenter"),
                "--target", target_pulse,
                "--uts",
                "hostname",
                hostname_pulse,
            ]

            cmd_docker_compose_set_dynamic_hostnames.extend(
                [
                    *cmd_docker_compose_set_dynamic_hostname_worker,
                    "&&",
                    *cmd_docker_compose_set_dynamic_hostname_pulse,
                    "&&",
                ]
            )

        cmd_compose_up_and_hostname = [
            *cmd_docker_compose_up,
            "&&",
            *cmd_docker_compose_set_dynamic_hostnames,
            # "&&",
            *cmd_docker_compose_logs,
        ]

        # What we have atm:
        # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target '$(docker inspect -f '"'"'{{ .State.Pid }}'"'"' deadline-10-2-worker-001)' --uts hostname ''"'"'$(hostname)-my-new-hostname'"'"'' && /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker logs --follow
        # Should be like:
        # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname)-my-new-hostname" && /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker logs --follow
        # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname $(hostname)-my-new-hostname-1234 && /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker logs --follow

        yield Output(cmd_compose_up_and_hostname)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "cmd_compose_up_and_hostname": MetadataValue.path(
                    " ".join(
                        shlex.quote(s) if not s in [
                            "&&",
                            ";",
                            *exclude_from_quote,
                        ] else s
                        for s in cmd_compose_up_and_hostname
                    )
                ),
                "compose_worker_runner_services": MetadataValue.json(compose_worker_runner_services),
                "compose_pulse_runner_services": MetadataValue.json(compose_pulse_runner_services),
            },
        )


    group_out = AssetsDefinition.from_op(
        op_group_out,
        can_subset=True,
        group_name=GROUP_COMPOSE_WORKER,
        key_prefix=KEY_COMPOSE_WORKER,
        keys_by_input_name={
            "compose": AssetKey([*KEY_COMPOSE_WORKER, "compose"]),
            "env": AssetKey([*KEY_COMPOSE_WORKER, "env"]),
            "group_in": AssetKey([*KEY_BASE, "group_out"]),
        },
    )


    docker_compose_graph = AssetsDefinition.from_op(
        op_docker_compose_graph,
        group_name=GROUP_COMPOSE_WORKER,
        key_prefix=KEY_COMPOSE_WORKER,
        keys_by_input_name={
            "group_out": AssetKey([*KEY_COMPOSE_WORKER, "group_out"]),
            "compose_project_name": AssetKey([*KEY_COMPOSE_WORKER, "compose_project_name"]),
        },
    )
