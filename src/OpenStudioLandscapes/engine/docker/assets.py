import pathlib
import shlex
import shutil
import textwrap
from typing import Generator

from python_on_whales import docker, Builder
import docker as docker_py
from docker.types.services import Mount

from dagster import (
    AssetExecutionContext,
    AssetMaterialization,
    MetadataValue,
    Output,
    asset,
    AssetIn,
    AssetKey,
)

from OpenStudioLandscapes.engine.constants import *
from OpenStudioLandscapes.engine.enums import *
from OpenStudioLandscapes.engine.utils import *


"""
buildkit.toml
# https://docs.docker.com/build/buildkit/

# cat > ~/.config/buildkit/buildkitd.toml << EOF

sudo bash -c 'mkdir -p /etc/buildkit

cat > /etc/buildkit/buildkitd.toml << EOF
insecure-entitlements = [ "network.host", "security.insecure" ]

EOF'


# sudo -s << EOF
# rm -f -- /tmp/installbuilder_installer*.log
# 
# export PACKAGE=Deadline-10.4.0.10-linux-installers
# ${NFS_INSTALLERS_ROOT}/${PACKAGE}/DeadlineClient-10.4.0.10-linux-x64-installer.run \
#     --mode unattended \
#     --prefix /opt/Thinkbox/Deadline10 \
#     --connectiontype Remote \
#     --proxyrootdir ${IP_MASTER}:${DEADLINE_RCS_PORT_TLS} \
#     --proxycertificate /nfs/deadline/Deadline10/certs/certs/Deadline10RemoteClient.pfx \
#     --proxycertificatepassword $DEADLINE_RCS_CERTIFICATE_PASSWORD \
#     --remotecontrol NotBlocked \
#     --blockautoupdateoverride NotBlocked \
#     --launcherservicedelay 30 30 &
#     
# while [[ ! -f /tmp/installbuilder_installer.log ]]; do sleep 1; done; tail -f /tmp/installbuilder_installer.log | grep -E --color=always '|^Script exit code: 1|^Executing ' &
# 
# EOF
"""


@asset(
    **ASSET_HEADER_BASE,
)
def run_builder(
    context: AssetExecutionContext,
) -> Generator[Output[Builder] | AssetMaterialization, None, None]:

    _builder = None
    builder_name = "openstudiolandscapes-builder"

    builders = docker.buildx.list()
    context.log.info(builders)

    for builder_ in builders:
        if builder_.name == builder_name:
            _builder = builder_

    buildkitd_flags = [
        "--allow-insecure-entitlement=network.host",
        "--allow-insecure-entitlement=security.insecure",
    ]

    if _builder is None:
        builder: Builder = docker.buildx.create(
            driver="docker-container",
            name=builder_name,
            bootstrap=True,
            platforms=["linux/amd64"],
            buildkitd_flags=shlex.join(buildkitd_flags),
            config=pathlib.Path(__file__).parent / "builder.toml"
        )
    else:
        builder: Builder = _builder

    cmd_inspect = [
        shutil.which("docker"),
        "buildx",
        "inspect",
        "--builder",
        # "--bootstrap",  # ensure builder has stopped before inspect
        builder_name,
    ]

    cmd_rm = [
        shutil.which("docker"),
        "buildx",
        "rm",
        builder_name,
    ]

    yield Output(builder)

    yield AssetMaterialization(
        asset_key=context.asset_key,
        metadata={
            "__".join(context.asset_key.path): MetadataValue.path(str(builder)),
            "dir": MetadataValue.json(dir(builder)),
            "buildkitd_flags": MetadataValue.json(buildkitd_flags),
            "name": MetadataValue.path(builder.name),
            "inspect": MetadataValue.path(shlex.join(cmd_inspect)),
            "rm": MetadataValue.path(shlex.join(cmd_rm)),
        },
    )
