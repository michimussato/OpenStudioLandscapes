#!/usr/bin/env bash


export PYTHON_MAJ="3"
export PYTHON_MIN="11"
export PYTHON_PAT="11"


apt-get update
apt-get upgrade

apt-get install -y openssh-server

# Set root password
# sudo su root
# passwd

sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

systemctl enable --now ssh

apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

pushd $(mktemp -d)

curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}

./configure --enable-optimizations
make -j $(nproc)
make altinstall

popd

# Install Docker
# https://docs.docker.com/engine/install/ubuntu/
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

# Required while not public
# # 1. https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
# ssh-keygen -t ed25519 -C "michimussato@gmail.com"
# eval "$(ssh-agent -s)"
# ssh-add ~/.ssh/id_ed25519
# # 2. https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account
# # 3. https://github.com/settings/keys
# cat ~/.ssh/id_ed25519.pub
# ssh-keyscan github.com >> ~/.ssh/known_hosts

mkdir -p ~/git/repos
git -C ~/git/repos clone git@github.com:michimussato/OpenStudioLandscapes.git

cd ~/git/repos/OpenStudioLandscapes
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .[dev]

nox -s clone_features
nox -s install_features_into_engine

nox --sessions pi_hole_prepare
nox --session harbor_prepare
