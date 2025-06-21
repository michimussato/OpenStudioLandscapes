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

from OpenStudioLandscapes.engine.base.ops import (
    op_docker_compose_graph,
)
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *

# # Todo:
# #  - [ ] Find a procedural way to deal with this
# from OpenStudioLandscapes.Deadline_10_2_Worker.constants import ASSET_HEADER as ASSET_HEADER_WORKER

from OpenStudioLandscapes.engine.common_assets.group_out import get_group_out


# Todo:
#  - [ ] get assets from common_assets


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
        "env_base": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_WORKER['key_prefix'], "env_base"])),
        "DOCKER_COMPOSE": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_WORKER['key_prefix'], "DOCKER_COMPOSE"])),
        },
    )
    def env(
        context: AssetExecutionContext,
        env_base: dict,
        DOCKER_COMPOSE: pathlib.Path,  # pylint: disable=redefined-outer-name
    ) -> Generator[Output[dict] | AssetMaterialization, None, None]:

        env_in = copy.deepcopy(env_base)

        env_in.update(
            expand_dict_vars(
                dict_to_expand={
                    "DOCKER_COMPOSE": DOCKER_COMPOSE.as_posix()
                },
                kv=env_in,
            )
        )

        env_in.update(
            {
                "COMPOSE_SCOPE": ComposeScope.WORKER,
            }
        )

        yield Output(env_in)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(env_in),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_WORKER['key_prefix'], "features_in"])),
        },
    )
    def env_base(
        context: AssetExecutionContext,
        features_in: dict,
    ) -> Generator[Output[dict] | AssetMaterialization, None, None]:

        context.log.info(features_in)

        _env_base = features_in.pop("env_base", {})

        yield Output(_env_base)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(_env_base),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_WORKER['key_prefix'], "features_in"])),
        },
    )
    def docker_config_json(
        context: AssetExecutionContext,
        features_in: dict,
    ) -> Generator[Output[pathlib.Path] | AssetMaterialization, None, None]:

        context.log.info(features_in)

        docker_config_json = features_in.pop("docker_config_json")

        yield Output(docker_config_json)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.path(docker_config_json),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_WORKER['key_prefix'], "features_in"])),
        },
    )
    def docker_config(
        context: AssetExecutionContext,
        features_in: dict,
    ) -> Generator[Output[DockerConfig] | AssetMaterialization, None, None]:

        context.log.info(features_in)

        _docker_config: DockerConfig = features_in.pop("docker_config")
        context.log.info(_docker_config)

        yield Output(_docker_config)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                _docker_config.name: MetadataValue.json(_docker_config.value),
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
        features_in.pop("docker_config_json", {})

        DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
        DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

        compose_files = []

        for feature, data in features_in.items():
            context.log.info(f"{features_in[feature] = }")
            compose_files.append(features_in[feature]["compose_yaml"])

        rel_paths = []
        dot_landscapes = pathlib.Path(env["DOT_LANDSCAPES"])

        # Convert absolute paths in `include` to
        # relative ones
        for path in compose_files:
            rel_path = get_relative_path_via_common_root(
                context=context,
                path_src=DOCKER_COMPOSE,
                path_dst=pathlib.Path(path),
                path_common_root=dot_landscapes,
            )

            rel_paths.append(rel_path.as_posix())

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
            "features_in": AssetIn(AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "features_in"])),
        },
    )
    def worker_composes(
        context: AssetExecutionContext,
        features_in: dict,
    ) -> Generator[Output[dict] | AssetMaterialization, None, None]:

        features_in.pop("env_base")
        features_in.pop("docker_config")
        features_in.pop("docker_config_json")

        compose_ = {}

        for key, value in features_in.items():

            compose_[key] = value.get("compose", {})

        context.log.info(compose_)

        yield Output(compose_)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(compose_),
            },
        )


    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "group_out_base": AssetIn(AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)])),
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
        docker_config_json: pathlib.Path = group_out_base["docker_config_json"]

        docker_compose_yaml: MutableMapping[str, str] = {}
        docker_compose: MutableMapping[str, Any] = {}

        for k, v in kwargs.items():
            # remove
            # - env_base
            # - constants_base
            # - features
            # - docker_config
            # - docker_config_json
            # from kwargs dicts
            for d in [
                "env_base",
                "constants_base",
                "features",
                "docker_config",
                "docker_config_json",
            ]:
                kwargs[k].pop(d)

            docker_compose_yaml[k] = str(kwargs[k]["compose_yaml"])
            docker_compose[k] = str(kwargs[k]["compose"])

        kwargs["env_base"] = env_base
        kwargs["docker_config"] = docker_config
        kwargs["docker_config_json"] = docker_config_json

        yield Output(kwargs)

        kwargs_serialized = copy.deepcopy(kwargs)

        serialize_dict(
            context=context,
            d=kwargs_serialized,
        )

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(kwargs_serialized),
                "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
                "docker_compose": MetadataValue.json(docker_compose),
                **metadatavalues_from_dict(
                    context=context,
                    d_serialized=kwargs_serialized,
                ),
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
            "worker_composes": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "worker_composes"]),
            ),
        },
    )
    def compose_up_and_set_hostname(
            context: AssetExecutionContext,
            env: dict,  # pylint: disable=redefined-outer-name
            cmd_docker_compose_up_dict: dict[str, list],  # pylint: disable=redefined-outer-name,
            worker_composes: dict,  # pylint: disable=redefined-outer-name,
    ):

        # Todo:
        #  - [x] for i in range(NUM_SERVICES): [...]

        compose_services = list(worker_composes["OpenStudioLandscapes_Deadline_10_2_Worker"]["services"].keys())

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
        for service_name in compose_services:

            target_worker = "$(docker inspect -f '{{ .State.Pid }}' %s)" % "--".join([service_name, env.get("LANDSCAPE", "default")])
            hostname_worker = f"$(hostname)-{service_name}"

            exclude_from_quote.extend(
                [
                    target_worker,
                    hostname_worker,
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

            cmd_docker_compose_set_dynamic_hostnames.extend(
                [
                    *cmd_docker_compose_set_dynamic_hostname_worker,
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
                "compose_runner_services": MetadataValue.json(compose_services),
            },
        )


    group_out = get_group_out(
        ASSET_HEADER=ASSET_HEADER_COMPOSE_WORKER,
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
