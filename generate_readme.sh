#!/usr/bin/env bash

# This script updates the README.md files
# of all OpenStudioLandscapes-Modules based on
# the template in
# OpenStudioLandscapes/src/OpenStudioLandscapes/engine/utils/markdown.py


export OSL_ROOT=~/git/repos


for dir in ${OSL_ROOT}/OpenStudioLandscapes-*/; do
    pushd ${dir}
    source .venv/bin/activate
    python3.11 generate_readme.py
    deactivate
    popd
done;
