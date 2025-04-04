#!/usr/bin/env bash

# This script updates the README.md files
# of all OpenStudioLandscapes-Modules based on
# the template in
# OpenStudioLandscapes/src/OpenStudioLandscapes/engine/utils/markdown.py


export OSL_ROOT=~/git/repos


for dir in "${OSL_ROOT}"/OpenStudioLandscapes-*/; do
    pushd "${dir}" || exit
    source .venv/bin/activate
    echo "activated."
    if [[ -f generate_readme.py ]]; then
        python3.11 generate_readme.py
    else
        echo "ERROR: generate_readme.py does not exist in ${dir}"
    fi;
    deactivate
    echo "deactivated."
    popd || exit
done;
