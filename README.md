

---

# deadline-docker

```
(type -p wget >/dev/null || (sudo apt update && sudo apt-get install wget -y)) \
	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
        && out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        && cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
	&& sudo apt update \
	&& sudo apt install gh -y
```

```
gh auth login
```

```
gh repo clone michimussato/deadline-docker
gh repo clone michimussato/git-crypt-keys
```

```
apt-get install -y git-crypt
cd /root/git/repos/deadline-docker
git-crypt unlock /root/git/repos/git-crypt-keys/deadline-docker.key
```

### Build Images

```
cd deadline-docker/10.2
./docker-build.sh
```

## 10.2

```
docker compose --project-name ddld_deadline-docker --file 10.2/docker-compose.yaml build --no-cache
docker compose --project-name ddld_deadline-docker --file 10.2/docker-compose.yaml up --remove-orphans --build
```

```
docker compose --file 10.2/docker-compose.yaml down
```

## Install Docker

https://docs.docker.com/engine/install/ubuntu/

```
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-doc
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
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Test

```
sudo docker run hello-world
```



# Dagster

```shell
cd ~/git/repos/deadline-docker
source .venv/bin/activate
export DAGSTER_HOME="$(pwd)/dagster/materializations"
dagster dev --workspace "$(pwd)/dagster/workspace.yaml" --host 0.0.0.0 --port 3000 
```