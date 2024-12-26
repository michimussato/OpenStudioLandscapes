#!/usr/bin/env bash


source /git/asdf/asdf.sh
cd /git/likec4/apps/playground || exit 1

# yarn dev --host 0.0.0.0 --port $LIKEC4_DEV_PORT_CONTAINER
"${@}"
