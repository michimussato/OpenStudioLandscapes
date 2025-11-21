import copy
import json
import operator
import pathlib
import shutil
import textwrap
from typing import Any, Dict, Generator, List, MutableMapping

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
from OpenStudioLandscapes.engine.common_assets.group_out import get_group_out
from OpenStudioLandscapes.engine.common_assets.scrape_networks import (
    get_scrape_networks,
)
from OpenStudioLandscapes.engine.compose_scopes.worker.constants import (
    ATTACH_SITE_TO_COMPOSE_SCOPE,
    COMPOSE_SCOPE,
)
from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.discovery.discovery import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *
from OpenStudioLandscapes.engine.utils.pangolin import *

# # Todo:
# #  - [ ] Find a procedural way to deal with this
# from OpenStudioLandscapes.Deadline_10_2_Worker.constants import ASSET_HEADER as ASSET_HEADER_WORKER


# Todo:
#  - [ ] get assets from common_assets


# https://github.com/yaml/pyyaml/issues/722#issuecomment-1969292770
yaml.SafeDumper.add_multi_representer(
    DockerComposeRestartPolicy,
    yaml.representer.SafeRepresenter.represent_str,
)


ins, feature_ins = get_dynamic_ins(
    compose_scope_filter=[COMPOSE_SCOPE],
    imported_features=IMPORTED_FEATURES,
    operator=operator.eq,
)


if bool(ins):

    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "env_base": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "env_base"])
            ),
            "DOCKER_COMPOSE": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "DOCKER_COMPOSE"])
            ),
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
                dict_to_expand={"DOCKER_COMPOSE": DOCKER_COMPOSE.as_posix()},
                kv=env_in,
            )
        )

        env_in.update(
            {
                "COMPOSE_SCOPE": COMPOSE_SCOPE,
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
            "features_in": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "features_in"])
            ),
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
            "features_in": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "features_in"])
            ),
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
                "__".join(context.asset_key.path): MetadataValue.path(
                    docker_config_json
                ),
            },
        )

    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "features_in": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "features_in"])
            ),
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
            "scrape_networks": AssetIn(
                AssetKey(
                    [*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "scrape_networks"]
                ),
            ),
        },
        description=textwrap.dedent(
            f"""
            Environment variable `OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE` 
            is set to `{ATTACH_SITE_TO_COMPOSE_SCOPE}`.
            
            If `OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE` is `True`,
            set the following environment variables before launching the Landscape:
            
            ```shell
            OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{COMPOSE_SCOPE.upper()}__NEWT_ID
            OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{COMPOSE_SCOPE.upper()}__NEWT_SECRET
            OPENSTUDIOLANDSCAPES__PANGOLIN_SITE__COMPOSE_SCOPE_{COMPOSE_SCOPE.upper()}__PANGOLIN_ENDPOINT
            ```
            """
        ),
    )
    def compose(
        context: AssetExecutionContext,
        env: dict,  # pylint: disable=redefined-outer-name
        features_in: dict,  # pylint: disable=redefined-outer-name
        scrape_networks: dict,  # pylint: disable=redefined-outer-name
    ) -> Generator[
        Output[MutableMapping[str, List[MutableMapping[str, List]]]]
        | AssetMaterialization,
        None,
        None,
    ]:
        """ """

        features_in.pop("env_base", {})
        features_in.pop("docker_config", {})
        features_in.pop("docker_image", {})
        features_in.pop("docker_config_json", {})

        DOCKER_COMPOSE = pathlib.Path(env["DOCKER_COMPOSE"])
        DOCKER_COMPOSE.parent.mkdir(parents=True, exist_ok=True)

        compose_files = []
        _compose_networks = set()

        for feature, data in features_in.items():
            context.log.info(f"{features_in[feature] = }")
            compose_file = features_in[feature]["compose_yaml"]
            compose_files.append(compose_file)

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

        docker_dict_include: Dict = {
            "include": [
                {
                    "path": rel_paths,
                },
            ],
        }

        if ATTACH_SITE_TO_COMPOSE_SCOPE:

            add_newt_service_to_compose_scope(
                scrape_networks=scrape_networks,
                docker_dict_include=docker_dict_include,
                compose_scope=COMPOSE_SCOPE,
            )

        docker_yaml_include = yaml.safe_dump(docker_dict_include)

        # Write docker-compose.yaml
        with open(DOCKER_COMPOSE, mode="w", encoding="utf-8") as fw:
            fw.write(docker_yaml_include)

        yield Output(docker_dict_include)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(
                    docker_dict_include
                ),
                "docker_yaml": MetadataValue.md(f"```yaml\n{docker_yaml_include}\n```"),
                "OPENSTUDIOLANDSCAPES__ATTACH_SITE_TO_COMPOSE_SCOPE": MetadataValue.bool(
                    ATTACH_SITE_TO_COMPOSE_SCOPE,
                ),
            },
        )

    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={
            "features_in": AssetIn(
                AssetKey([*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "features_in"])
            ),
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
            "group_out_base": AssetIn(
                AssetKey([*ASSET_HEADER_BASE["key_prefix"], str(GroupIn.BASE_IN)])
            ),
            **feature_ins,
        },
    )
    def features_in(
        context: AssetExecutionContext,
        group_out_base: dict,  # pylint: disable=redefined-outer-name
        **kwargs,
    ) -> Generator[
        Output[MutableMapping[str, List[MutableMapping[str, List]]]]
        | AssetMaterialization,
        None,
        None,
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

        kwargs_json = json.dumps(kwargs, default=str)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(kwargs_json),
                "docker_compose_yaml": MetadataValue.json(docker_compose_yaml),
                "docker_compose": MetadataValue.json(docker_compose),
                **metadatavalues_from_dict(
                    context=context,
                    d_serialized=kwargs_json,
                ),
            },
        )

    @asset(
        **ASSET_HEADER_COMPOSE_WORKER,
        ins={},
    )
    def cmd_extend(
        context: AssetExecutionContext,
    ) -> Generator[Output[list[Any]] | AssetMaterialization | Any, Any, None]:

        ret = ["--detach"]

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
            "composes": AssetIn(
                AssetKey(
                    [*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "worker_composes"]
                ),
            ),
        },
    )
    def cmd_append(
        context: AssetExecutionContext,
        env: dict,  # pylint: disable=redefined-outer-name
        composes: dict,  # pylint: disable=redefined-outer-name,
    ) -> Generator[
        Output[dict[str, list[Any]]] | AssetMaterialization | Any, Any, None
    ]:

        ret = {"cmd": [], "exclude_from_quote": []}

        # Todo
        #  - [ ] find a better solution for this hardcoded logic
        if "OpenStudioLandscapes_Deadline_10_2_Worker" in composes:

            compose_services = list(
                composes["OpenStudioLandscapes_Deadline_10_2_Worker"]["services"].keys()
            )

            # Example cmd:
            # /usr/bin/docker compose --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__group_out/docker_compose/docker-compose.yml --project-name 2025-04-08-10-45-09-df78673952cc4499a80407d91bd404f4-worker up --detach --remove-orphans && sudo nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001) --uts hostname "$(hostname -f)-nice-hack"

            # cmd_docker_compose_up.extend(
            #     [
            #         # needs to be detached in order to get to do sudo
            #         "--detach",
            #     ]
            # )

            exclude_from_quote = []

            cmd_docker_compose_set_dynamic_hostnames = []

            # Transform container hostnames
            # - deadline-10-2-worker-001...nnn
            # - deadline-10-2-pulse-worker-001...nnn
            # into
            # - $(hostname)-deadline-10-2-worker-001...nnn
            # - $(hostname)-deadline-10-2-pulse-worker-001...nnn
            for service_name in compose_services:

                target_worker = (
                    "$(docker inspect -f '{{ .State.Pid }}' %s)"
                    % "--".join([service_name, env.get("LANDSCAPE", "default")])
                )
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
                    "--target",
                    target_worker,
                    "--uts",
                    "hostname",
                    hostname_worker,
                ]

                # Reference:
                # /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-worker-001 && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-pulse-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-pulse-worker-001 \
                # /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-pulse-worker-001--2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754) --uts hostname $(hostname)-deadline-10-2-pulse-worker-001 && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001--2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754) --uts hostname $(hostname)-deadline-10-2-worker-001
                #     && /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa-worker logs --follow
                # Current:
                # Pre
                # /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa/Deadline_10_2_Worker__Deadline_10_2_Worker/Deadline_10_2_Worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target '$(docker inspect -f '"'"'{{ .State.Pid }}'"'"' deadline-10-2-pulse-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa)' --uts hostname '$(hostname)-deadline-10-2-pulse-worker-001' && /usr/bin/sudo /usr/bin/nsenter --target '$(docker inspect -f '"'"'{{ .State.Pid }}'"'"' deadline-10-2-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa)' --uts hostname '$(hostname)-deadline-10-2-worker-001'
                # Post
                #                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-pulse-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-pulse-worker-001 && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001--2025-07-23-00-51-15-1afae50517c5453b95c518ee0cd8e0aa) --uts hostname $(hostname)-deadline-10-2-worker-001
                # /usr/bin/docker --config /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754/OpenStudioLandscapes_Base__OpenStudioLandscapes_Base/OpenStudioLandscapes_Base__docker_config_json compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754/ComposeScope_worker__ComposeScope_worker/ComposeScope_worker__DOCKER_COMPOSE/docker_compose/docker-compose.yml --project-name 2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754-worker up --remove-orphans --detach && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-pulse-worker-001--2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754) --uts hostname $(hostname)-deadline-10-2-pulse-worker-001 && /usr/bin/sudo /usr/bin/nsenter --target $(docker inspect -f '{{ .State.Pid }}' deadline-10-2-worker-001--2025-07-23-18-45-54-adaf9bd52e514a7e8be265dec51a2754) --uts hostname $(hostname)-deadline-10-2-worker-001

                cmd_docker_compose_set_dynamic_hostnames.extend(
                    [
                        "&&",
                        *cmd_docker_compose_set_dynamic_hostname_worker,
                    ]
                )

            ret["cmd"].extend(cmd_docker_compose_set_dynamic_hostnames)
            ret["exclude_from_quote"].extend(exclude_from_quote)

        yield Output(ret)

        yield AssetMaterialization(
            asset_key=context.asset_key,
            metadata={
                "__".join(context.asset_key.path): MetadataValue.json(ret),
            },
        )

    group_out = get_group_out(
        ASSET_HEADER=ASSET_HEADER_COMPOSE_WORKER,
    )

    scrape_networks = get_scrape_networks(
        ASSET_HEADER=ASSET_HEADER_COMPOSE_WORKER,
    )

    docker_compose_graph = AssetsDefinition.from_op(
        op_docker_compose_graph,
        group_name=ASSET_HEADER_COMPOSE_WORKER["group_name"],
        key_prefix=ASSET_HEADER_COMPOSE_WORKER["key_prefix"],
        keys_by_input_name={
            "group_out": AssetKey(
                [*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "group_out"]
            ),
            "compose_project_name": AssetKey(
                [*ASSET_HEADER_COMPOSE_WORKER["key_prefix"], "compose_project_name"]
            ),
        },
    )
