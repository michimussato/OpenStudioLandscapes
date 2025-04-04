#!/usr/bin/env bash


export OSL_ROOT=~/git/repos


for dir in ${OSL_ROOT}/OpenStudioLandscapes-*/; do
    pushd ${dir}
    source .venv/bin/activate
    python3.11 generate_readme.py
    deactivate
    popd
done;
