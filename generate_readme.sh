#!/usr/bin/env bash

# This script updates the README.md files
# of all OpenStudioLandscapes-Modules based on
# the template in
# OpenStudioLandscapes/src/OpenStudioLandscapes/engine/utils/markdown.py


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# The script assumes that all module repos live in the same root dir
# as this one


for dir in "${SCRIPT_DIR}"/../OpenStudioLandscapes-*/; do
    pushd "${dir}" || exit
    source .venv/bin/activate
    echo "activated."
    if [[ -f generate_readme.py ]]; then
        echo "Updating ${dir}README.md..."
        python3.11 generate_readme.py
        echo "Update done."
    else
        echo "ERROR: generate_readme.py does not exist in ${dir}"
    fi;
    deactivate
    echo "deactivated."
    popd || exit
done;
