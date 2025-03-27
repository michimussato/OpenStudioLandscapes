#!/usr/bin/env bash


# TOC
# max-concurrent-uploads:
# # Limit concurrent uploads:
# # - https://stackoverflow.com/a/48348339
# features:
# # https://docs.docker.com/build/buildkit/#getting-started


sudo bash -c 'mkdir -p /etc/docker

cat > /etc/docker/daemon.json << EOF
{
  "features": {
    "buildkit": true
  },
  "max-concurrent-uploads": 1,
  "insecure-registries" : [
    "http://harbor.farm.evil:80",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    "http://10.1.2.15:5000",
    "http://[::1]:5000"
  ]
}

EOF'

sudo systemctl daemon-reload
sudo systemctl restart docker
