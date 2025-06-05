#!/bin/env bash


# Documentation:
# https://docs.docker.com/engine/install/ubuntu/

for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do
    apt-get remove $pkg
done

apt autoremove -y

apt-get update

apt-get install --no-install-recommends -y ca-certificates curl

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

mkdir -p /etc/docker
touch /etc/docker/daemon.json
cat > /etc/docker/daemon.json << EOF
{
  "insecure-registries": [
    "http://harbor.farm.evil:80"
  ],
  "max-concurrent-uploads": 1
}
EOF


echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update

apt-get install --no-install-recommends -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# https://docs.docker.com/engine/install/linux-postinstall/

# groupadd --force docker
# usermod --append --groups docker "openstudiolandscapes"

# systemctl daemon-reload
# systemctl restart docker

# sudo rm -rf /home/user/temp/OpenStudioLandscapes/.landscapes/.harbor/bin/*
# sudo rm -rf /home/user/temp/OpenStudioLandscapes/.landscapes/.harbor/data/*

echo "Your /etc/docker/daemon.json file looks like:"
cat /etc/docker/daemon.json

exit 0
