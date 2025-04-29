#!/usr/bin/env bash
# https://www.baeldung.com/linux/curl-fetched-script-arguments


# https://itsfoss.com/could-not-get-lock-error/
# stat /var/lib/dpkg/lock
# stat /var/lib/dpkg/lock-frontend
# ps aux | grep -i apt

if ! sudo apt-get upgrade -y; then
    echo "Update in progress in the background."
    echo "Let the process finish and run this script afterwards."
    exit 1
fi;

# Install Python 3.11
export PYTHON_MAJ="3"
export PYTHON_MIN="11"
export PYTHON_PAT="11"

sudo apt-get install -y \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    wget \
    pkg-config \
    liblzma-dev \
    libbz2-dev \
    libsqlite3-dev \
    curl

pushd "$(mktemp -d)" || exit

curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} || exit

./configure --enable-optimizations
make -j "$(nproc)"
sudo make altinstall

popd || exit

# Install Docker
# # https://docs.docker.com/engine/install/ubuntu/
for pkg in \
    docker.io \
    docker-doc \
    docker-compose \
    docker-compose-v2 \
    podman-docker \
    containerd \
    runc\
    ; do sudo apt-get remove $pkg; done
sudo apt autoremove -y

sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add trust for insecure harbor.farm.evil
#read -e -p "Do you want me to configure /etc/docker/daemon.json?" choice
#[[ "$choice" == [Yy]* ]] \
#    && sudo -s << EOF
#mkdir -p /etc/docker
#touch /etc/docker/daemon.json
#cat > /etc/docker/daemon.json
#{
#  "insecure-registries" : [
#    "http://harbor.farm.evil:80"
#  ],
#  "max-concurrent-uploads": 1
#}
#EOF
#|| echo "Ok, I didn't."
sudo -s << EOF
mkdir -p /etc/docker
touch /etc/docker/daemon.json
cat > /etc/docker/daemon.json
{
  "insecure-registries" : [
    "http://harbor.farm.evil:80"
  ],
  "max-concurrent-uploads": 1
}
EOF

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# # https://docs.docker.com/engine/install/linux-postinstall/
sudo groupadd --force docker
sudo usermod --append --groups docker "$USER"

sudo systemctl daemon-reload
sudo systemctl restart docker

# Install OpenStudioLandscapes
sudo apt-get install -y graphviz
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools setuptools_scm wheel
pip install -e .[dev]

nox -s clone_features
nox -s install_features_into_engine

deactivate

read -r -e -p "Do you want me to add entries to /etc/hosts?" choice
[[ "$choice" == [Yy]* ]] \
    && sudo sed -i -e '$a127.0.0.1    dagster.farm.evil' -e '/127.0.0.1    dagster.farm.evil/d' /etc/hosts \
    && sudo sed -i -e '$a127.0.0.1    postgres-dagster.farm.evil' -e '/127.0.0.1    postgres-dagster.farm.evil/d' /etc/hosts \
    && sudo sed -i -e '$a127.0.0.1    harbor.farm.evil' -e '/127.0.0.1    harbor.farm.evil/d' /etc/hosts \
|| echo "Ok, I didn't."

echo ""
echo "Your /etc/hosts file looks like:"
sudo cat /etc/hosts
echo ""

echo ""
echo "Your /etc/docker/daemon.json file looks like:"
sudo cat /etc/docker/daemon.json
echo ""

echo "Reboot system please."

exit 0
