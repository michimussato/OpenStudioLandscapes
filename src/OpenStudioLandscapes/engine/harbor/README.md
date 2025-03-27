

---

# Harbor

- https://medium.com/@Shamimw/setting-up-harbor-docker-registry-installation-and-pushing-docker-images-a8b3db6fca6a
- https://www.youtube.com/watch?v=o2vhyZO8A8I

```
wget https://github.com/goharbor/harbor/releases/download/v2.12.2/harbor-offline-installer-v2.12.2.tgz

tar xvf harbor-offline-installer-v2.12.2.tgz

cd harbor

vi harbor.yml

vi /etc/docker/daemon.json
#{
#    "log-level":        "error",
#    "insecure-registries": ["your server:8086"]
#}

sudo systemctl restart docker.service

sudo ./install.sh
```