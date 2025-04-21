import copy
import os
import pathlib
import shlex
import shutil
from typing import Generator, List, MutableMapping, Any

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
from OpenStudioLandscapes.Deadline_10_2_Worker.constants import ASSET_HEADER as ASSET_HEADER_WORKER


# Dynamic inputs based on the imported
# third party code locations
ins = {}
feature_ins = {}
for i in IMPORTED_FEATURES:
    # ex: module = "OpenStudioLandscapes.Ayon.definitions"
    module = i["module"]
    compose_scope = i["compose_scope"]
    if compose_scope == ComposeScope.WORKER:
        split = module.split(".")
        key = split[1]  # key = "Ayon"
        ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "group_out"]))
        feature_ins[f"{split[0]}_{split[1]}"] = AssetIn(AssetKey([key, "feature_out"]))


if bool(ins):
    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "group_in": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out"])),
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
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "env"]),
            ),
            "features_in": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "features_in"]),
            ),
        },
    )
    def compose(
        context: AssetExecutionContext,
        env: dict,  # pylint: disable=redefined-outer-name
        features_in: dict,  # pylint: disable=redefined-outer-name
    ) -> Generator[
        Output[MutableMapping[str, List[MutableMapping[str, List]]]] | AssetMaterialization, None, None
    ]:
        """ """

        features_in.pop("env_base", {})
        features_in.pop("docker_config", {})
        features_in.pop("docker_image", {})

        DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
        DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

        compose_files = []

        for feature, data in features_in.items():
            context.log.info(features_in[feature])
            compose_files.append(features_in[feature]["compose_yaml"])

        # Convert absolute paths in `include` to
        # relative ones
        # DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
        # DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

        rel_paths = []
        dot_landscapes = pathlib.Path(env["DOT_LANDSCAPES"])

        for path in compose_files:
            start_dir = DOCKER_COMPOSE.parent

            levels = start_dir.as_posix().split(dot_landscapes.as_posix())[-1].split(os.sep)[1:]
            context.log.info(levels)
            context.log.info(path.split(os.sep)[1:][6:])
            _rel_path = "../" * len(levels) + "/".join(path.split(os.sep)[1:][6:])
            context.log.info(_rel_path)

            rel_paths.append(_rel_path)

        docker_dict_include = {
            "include": [
                {
                    "path": rel_paths,
                },
            ],
        }

        docker_yaml_include = yaml.dump(docker_dict_include)

        # Write docker-compose.yaml
        with open(DOCKER_COMPOSE, mode="w", encoding="utf-8") as fw:
            fw.write(docker_yaml_include)

        yield Output(docker_dict_include)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(docker_dict_include),
                "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml_include}\n```"),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "group_out_base": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out"])),
            **feature_ins,
        },
    )
    def features_in(
        context: AssetExecutionContext,
        group_out_base: dict,  # pylint: disable=redefined-outer-name
        **kwargs,
    ) -> Generator[
        Output[MutableMapping[str, List[MutableMapping[str, List]]]] | AssetMaterialization, None, None
    ]:
        """ """

        context.log.info(kwargs)

        env_base = group_out_base["env_base"]
        docker_config: DockerConfig = group_out_base["docker_config"]

        docker_compose_yaml: MutableMapping[str, str] = {}
        docker_compose: MutableMapping[str, Any] = {}

        for k, v in kwargs.items():
            # remove
            # - env_base
            # - constants_base
            # - features
            # - docker_config
            # from kwargs dicts
            for d in [
                "env_base",
                "constants_base",
                "features",
                "docker_config",
            ]:
                kwargs[k].pop(d)

            docker_compose_yaml[k] = str(kwargs[k]["compose_yaml"])
            docker_compose[k] = str(kwargs[k]["compose"])

        kwargs["env_base"] = env_base
        kwargs["docker_config"] = docker_config

        metadata = {}

        out_ = copy.deepcopy(kwargs)

        # JSON cannot serialize certain types
        # out of the box. This makes sure that
        # MetadataValue.json receives only
        # serializable input.
        def _serialize(d):
            for k_, v_ in d.items():
                if isinstance(v_, MutableMapping):
                    _serialize(v_)
                elif isinstance(v_, pathlib.PosixPath):
                    d[k_] = v_.as_posix()
                else:
                    d[k_] = str(v_)

        _serialize(out_)

        for k, v in out_.items():
            context.log.warning(k)
            context.log.warning(v)
            metadata[k] = MetadataValue.json(v)

        yield Output(kwargs)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(out_),
                "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
                "docker_compose": MetadataValue.json(docker_compose),
                **metadata,
            },
        )


    # Todo:
    #  - [ ] This is a bit hacky. Maybe there is a better way
    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "env": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "env"]),
            ),
            "cmd_docker_compose_up_dict": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "cmd_docker_compose_up"]),
            ),
            "compose_pulse_runner": AssetIn(
                AssetKey([*ASSET_HEADER_WORKER["key_prefix"], "compose_pulse_runner"]),
            ),
            "compose_worker_runner": AssetIn(
                AssetKey([*ASSET_HEADER_WORKER["key_prefix"], "compose_worker_runner"]),
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
        group_name=ASSET_HEADER_COMPOSE_WORKER["group_name"],
        key_prefix=ASSET_HEADER_COMPOSE_WORKER["key_prefix"],
        keys_by_input_name={
            "compose": AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "compose"]),
            "env": AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "env"]),
            "group_in": AssetKey([*ASSET_HEADER_BASE["key_prefix"], "group_out"]),
        },
    )


    docker_compose_graph = AssetsDefinition.from_op(
        op_docker_compose_graph,
        group_name=ASSET_HEADER_COMPOSE_WORKER["group_name"],
        key_prefix=ASSET_HEADER_COMPOSE_WORKER["key_prefix"],
        keys_by_input_name={
            "group_out": AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "group_out"]),
            "compose_project_name": AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "compose_project_name"]),
        },
    )
