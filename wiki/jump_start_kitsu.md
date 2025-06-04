Requirements:  
- `python3.11`  
- `git`  
- `graphviz`  
- `docker`  
- `docker compose`  
  
```shell  
git clone https://github.com/michimussato/OpenStudioLandscapesgit -C OpenStudioLandscapes/.features/ clone https://github.com/michimussato/OpenStudioLandscapes-Kitsu  
cd OpenStudioLandscapes  
nox --session create_venv_engine  # installs OpenStudioLandscapes[dev] into venvnox --session install_features_into_engine  
nox --session harbor_preparenox --session harbor_up_detach```  
  
Open Harbor URL:  
http://localhost:80  
  
Create `[x] Public` project `openstudiolandscapes`.  
(You can delete `library`)  
  
![harbor_create_project.png](_images/harbor_create_project.png)  
![harbor_new_project.png](_images/harbor_new_project.png)  
  
```shell  
nox --session dagster_postgres```  
  
![dagster_webserver.png](../_images/dagster_webserver.png)  
  
Open Dagster URL:  
http://localhost:3000/asset-groups  
  
![dagster_tldr.svg](../_images/dagster_tldr.svg)  
  
In Dagster, click `Materialize All`, and we will be presented with the following  
Landscape Map eventually:  
  
![Landscape_Map__tldr.svg](../_images/Landscape_Map__tldr.svg)  
  
alongside the following command:  
  
```shell  
/usr/bin/docker compose --file /home/michael/git/repos/OpSL_test/OpenStudioLandscapes/.landscapes/2025-04-13-00-46-55-37e03a603c434c27b735f876d55863f4/Compose_default__Compose_default/Compose_default__group_out/docker_compose/docker-compose.yml --project-name 2025-04-13-00-46-55-37e03a603c434c27b735f876d55863f4-default up --remove-orphans```  
  
Visit http://localhost:4545; lo and behold:  
  
![kitsu_landing.png](../_images/kitsu_landing_tldr.png)