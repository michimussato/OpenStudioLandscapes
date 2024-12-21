

---

# deadline-docker

```
git clone https://github.com/michimussato/deadline-docker
```

## 10.2

```
docker compose --file 10.2/docker-compose.yaml build --no-cache
docker compose --file 10.2/docker-compose.yaml up -d
docker compose --project-name ddld_deadline-docker --file 10.2/docker-compose.yaml up --remove-orphans --build
```

```
docker compose --file 10.2/docker-compose.yaml down
```