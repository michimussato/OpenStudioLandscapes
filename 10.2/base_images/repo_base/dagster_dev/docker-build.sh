#!/usr/bin/env bash

docker build  \
    --tag michimussato/dagster_dev:latest  \
    --build-arg PYTHON_MAJ=3  \
    --build-arg PYTHON_MIN=11  \
    --build-arg PYTHON_PAT=11  \
    .
