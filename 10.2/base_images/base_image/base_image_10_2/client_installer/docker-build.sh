#!/usr/bin/env bash

docker build  \
    --tag michimussato/client_installer_10_2:latest  \
    --build-arg DEADLINE_VERSION=10.2.1.1  \
    --build-arg INSTALLERS_ROOT=/data/share/nfs/installers  \
    .
