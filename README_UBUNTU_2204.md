```
sudo su root
passwd
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y openssh-server build-essential zlib1g-dev pkg-config

sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
# sudo systemctl restart ssh
sudo systemctl enable --now ssh
# sudo apt-get install -y python3.11 python3.11-venv git
```

Install Python 3.11.11

```
sudo apt-get install -y build-essential zlib1g-dev pkg-config libbz2-dev libsqlite3-dev liblzma-dev libssl-dev
sudo apt-get install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

export PYTHON_MAJ="3"
export PYTHON_MIN="11"
export PYTHON_PAT="11"
mkdir -p ~/python${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}
cd ~/python${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}
curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz
cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}
./configure --enable-optimizations
make -j $(nproc)
sudo make altinstall
```

```
python${PYTHON_MAJ}.${PYTHON_MIN} -m pip install pip --upgrade
```

```
# 1. https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
ssh-keygen -t ed25519 -C "michimussato@gmail.com"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
# 2. https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account
# 3. https://github.com/settings/keys
cat ~/.ssh/id_ed25519.pub
```

```
mkdir -p ~/git/repos
cd ~/git/repos
ssh-keyscan github.com >> ~/.ssh/known_hosts
git clone git@github.com:michimussato/OpenStudioLandscapes.git
cd OpenStudioLandscapes
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools
pip install -e .[dev]
```

```
nox -l
```

```
nox -s clone_features
nox -s pull_features
nox -s install_features_into_engine
```

```
# https://docs.docker.com/engine/install/ubuntu/
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
sudo apt autoremove -y
```

```
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

```
nox --sessions pi_hole_prepare
nox --session harbor_prepare
nox --sessions harbor_up_detach pi_hole_up_detach dagster_postgres_up_detach dagster_postgres
```

Go to Harbor, create project `openstudiolandscapes`.
