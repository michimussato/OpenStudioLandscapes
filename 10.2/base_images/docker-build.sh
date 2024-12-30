#!/usr/bin/env bash

#mkdir -p /data/share/nfs
#ln -sfn /data/share/nfs /nfs

./repo_base/docker-build.sh
./repo_base/repo_installer/docker-build.sh
./repo_base/client_installer/docker-build.sh
./repo_base/client_installer/generic_runner/docker-build.sh
./repo_base/likec4_dev/docker-build.sh
./repo_base/dagster_dev/docker-build.sh
