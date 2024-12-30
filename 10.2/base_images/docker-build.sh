#!/usr/bin/env bash

#mkdir -p /data/share/nfs
#ln -sfn /data/share/nfs /nfs

pushd repo_base || return
./docker-build.sh
popd || return

pushd repo_base/repo_installer || return
./docker-build.sh
popd || return

pushd repo_base/client_installer || return
./docker-build.sh
popd || return

pushd repo_base/client_installer/generic_runner || return
./docker-build.sh
popd || return

pushd repo_base/likec4_dev || return
./docker-build.sh
popd || return

pushd repo_base/dagster_dev || return
./docker-build.sh
popd || return
