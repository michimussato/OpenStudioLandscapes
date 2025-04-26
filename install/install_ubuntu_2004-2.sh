#!/usr/bin/env bash
# https://www.baeldung.com/linux/curl-fetched-script-arguments


apt-get upgrade -y

# Install Python 3.11
export PYTHON_MAJ="3"
export PYTHON_MIN="11"
export PYTHON_PAT="11"

apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget pkg-config liblzma-dev libbz2-dev libsqlite3-dev curl

pushd "$(mktemp -d)" || exit

curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} || exit

./configure --enable-optimizations
make -j "$(nproc)"
make altinstall

popd || exit

# Install Docker
# # https://docs.docker.com/engine/install/ubuntu/
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
apt autoremove -y

apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update

apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# # https://docs.docker.com/engine/install/linux-postinstall/
groupadd --force docker
usermod --append --groups docker "$USER"

# Install OpenStudioLandscapes
python3.11 -m pip install --upgrade pip setuptools --root-user-action ignore
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .[dev]

nox -s clone_features
nox -s install_features_into_engine

deactivate

exit 0
