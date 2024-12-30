#!/usr/bin/env bash

bash repo_base/docker-build.bash
bash repo_base/repo_installer/docker-build.sh
bash repo_base/client_installer/docker-build.sh
bash repo_base/client_installer/generic_runner/docker-build.sh
bash repo_base/likec4_dev/docker-build.sh
bash repo_base/dagster_dev/docker-build.sh
