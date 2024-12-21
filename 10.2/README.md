<!-- TOC -->
* [`deadline.ini`](#deadlineini)
* [Deadline Docker 10.2](#deadline-docker-102)
  * [Symlinks](#symlinks)
  * [Automated](#automated)
<!-- TOC -->

---

# `deadline.ini`

https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/manual/client-config.html#client-config-conn-server-ref-label

# Deadline Docker 10.2

```
sudo rm -rf /home/michael/git/repos/deadline-setup/deadline-setup-docker/10.2/DeadlineRepositoryInstall/*
sudo rm -rf /home/michael/git/repos/deadline-setup/deadline-setup-docker/10.2/DeadlineClientInstall/*
```

## Symlinks

> In general, symlinks do not work inside docker. I found this the hard way.

## Automated

- https://derlin.github.io/docker-compose-viz-mermaid/

```
cd ~/git/repos/deadline-docker
java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ./10.2/docker-compose.yaml --ilinks --theme DARK --ports --volumes --networks --format TEXT --dir TB --out ./10.2/mermaid/deadline-docker.mermaid
java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ./10.2/docker-third-party/ayon/docker-compose.override.yml --ilinks --theme DARK --ports --volumes --networks --format TEXT --dir TB --out ./10.2/mermaid/ayon-docker.mermaid
java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ./10.2/docker-third-party/cgwire/docker-compose.kitsu.yaml --ilinks --theme DARK --ports --volumes --networks --format TEXT --dir TB --out ./10.2/mermaid/kitus-docker.mermaid
# java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ../ayon-docker/docker-compose.yml --ilinks --theme DARK --ports --volumes --networks --format TEXT --dir TB --out ./10.2/mermaid/ayon-docker.mermaid


# Browser
# Editor starts with      https://mermaid-js.github.io/mermaid-live-editor/edit#
# Full screen starts with https://mermaid-js.github.io/mermaid-live-editor/view#
xdg-open $(java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ./10.2/docker-compose.yaml --ilinks --theme DARK --ports --volumes --networks --format editor --dir TB)
xdg-open $(java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ./10.2/docker-third-party/ayon/docker-compose.override.yml --ilinks --theme DARK --ports --volumes --networks --format editor --dir TB)
xdg-open $(java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ./10.2/docker-third-party/cgwire/docker-compose.kitsu.yaml --ilinks --theme DARK --ports --volumes --networks --format editor --dir TB)
# xdg-open $(java -jar docker-compose-viz-mermaid_no_local-1.3.0.jar ../ayon-docker/docker-compose.yml --ilinks --theme DARK --ports --volumes --networks --format editor --dir TB)
```

[./10.2/docker-compose.yaml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNrtWVtvozgU_ivIo6oZiTshFx5G2m73bVaLZkf7sE1VGTApWwIRkDadKP99zR2MwSST5mn6UIHPd75zfL5jQ8wB2KGDgAFubg5e4CUGd7hNntEG3RrcrQOjl9vj8eZmFbh--GY_wyjhvt-tAo77x4EJjPEACtw4QXGS3iuyGm6T789e8GKF-3sEHd8L0D22WDBGirwJg3WYAr_-9ftvXw-HFZDSOynjkTCRlDI9ZWOKLKoSZpNKOqnLJ2WEGcdTRrkCxyO3F0TuBE9OFPZcnpmFJ_BQXAqKLKiPnakeDkTKOGAarz1IcHZYMpcRuPMKe34F0H4boTiuyiAUAz3FGJx5zTVi-hRwmmbsej6yovAtRlHj0rHS3hGlCiY1jM1r0bGqlsDNRlqy-I3BLLYdBq637on8XxwGeewC1hs5RTZji10jNfwF5D9DfTKLvNPr9i7FGsq2rxuYPn3AosQOXONKRJmL8xZGL_EW2ugdbvy2EgXuKQdKFVJMoZkUuRIFrgPIciiMDnp9KPnw9WNvPsUNM5viti-XDcT_Peh7P2DihUHMSq4UKV_qZQEJe6vQ-x51mD4jgMN9-g1tw9hLwuhdkc_d85scjE2-Cc0TLwxRZfCCOIG-j6J0oyvNQm0XKsCJG99wqOHuP9F3uObnV5pZX6Kqtu-hIKFXNLcxqzm-fc6RvZvgyXKOpRjpV2wRdUFLPH4Ba28iNUQqMSIGNTaQVxhJvmfRZCJc2k1mx9EuCMgVYMdCPnyWUoP6kIuxkcCVG2IwNHNlM52ZHkPy_5yq252Pn51dXbPxaynbTuLK2jKCs9Qd4z7C5-MUTl8LUESRODdcS2MijSuLzIrOUnmU_xinD9QZWbipXj2btpxr49X07qZzbc1HZMDUfSzHSMf-xzwnCF9GvNDRt5CWM_0VYoQj-dihjZ8QiT6JjKB9fjFQsxPCsbz7Zkes0lMiDniS0Ro_VCkVIA40KAhTnkzUuazMP3_G_dY1K5PJQl7ImZXDVwpXgdoHJaaaIksW4vezqU0mmixX5vYPOHOKXfFfZe2Zq6mnuOWSxPWsiXomKby8fZCKC-mRWqEamUlSJdqxMLqRjqatzx7e1uKgY8g1R0d12qkHRuvzNpSoaD31B6m-zuva6ssWllJWwsiuLN2hp7g97GR96TBKielAWpV7kD2FbqJTvO3DGD_QXe419HcbFKc19Y1PsqtPp4iPkyh8QcYnVVvOFlaFv8SpHd_iGLr7KP7BA1eefS56mSwZk-fZp4I866BuRJDzXmwuxUkyXSqDoffVX_n9yu9j8yu31NY2uw2jpNxkdajP9Xm1yVozW3XdepM1Zd5UeFPlTY03p7yp584tugBVbJqrK5ZesS2UO-X-rmYrHqt8_QDInFcB4MEGRRvoOcAAh9RhBbIvoitg4Mv0m-gKrIIjxsFdEv79HtjASKId4kEU7tbPwHAhfnzxYLfFs0f3HlxHcFNCtjD4Nwyr2xzzh5Mm0IAA4wD2wFguRVXRtOVUmemytpRnPHgHhqIpoj7XFvJsPlNnS1078uBHximLiwXGqrKsKqo60xbYAWXcf-YfebNvvcf_AVt1u2U)
[./10.2/docker-third-party/ayon/docker-compose.override.yml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNqNk8uO2jAUhl_F8ggBUsC54JB40QWiy0ojtepiyCycxIFoEpvahkKjvHvtMAkEddGVz-U7_zm-NTATOYMETiZNyUtNQDPVB1azKQHTnMqPadtOJgkvKvE7O1CpwY9NwgH4yXRWiYxWuqxZ0yDjosFvW7BYgnEMLBcXcBRK7yVTu1lvzd87tZxqqow844WydkoVU_QqeM_9qmzYNLIL6lBkWDTAyNLojncZM8jFTnKmElVl-pwezWTneHVnMxyuo_ncbgC7rmuQL0AxeWbSAj1s0gsgmXFLLeR1h-426nYkWV6abXbL_P0Jt8BN8x-JUYta8L3I0x36NB7EH_NPgkPUxrOKKrVlBTiL6lQb3aKsKvLiFni1Yo7SUnww8uIHcRilAz--X-d_76fvMep7FFL3XTHFa7weuqZh5hfFveure6NH9ZwN5UGBvRQP5ZG38babe_n9IJ3PI-iKEw4dWDNZ0zI3L72xBQnsXnkCiTHtO09gwlvD0ZMW3688g0TLE3OgFKf9AZKCVsp4p6PZJtuWdC9p3SNHyt-EGNwb8zW3gzwgkDTwAkkcL30vCOKVF2I3iN3QgVdIvMBb4nUQueE69MMYB60D_3Sa7jKKDOvFUeBjP_R97EDWaX-7fdzu_7Z_AcbkSa0)
[./10.2/docker-third-party/cgwire/docker-compose.kitsu.yaml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNp1ksGOmzAQhl_FmlWUrETABkzAhx6q7bFSpFY9tO7BCyZBATvFps0W8e41RGSX7u4Jz8w384_N30OuCwkMVqu-UpVlqF_bo2zkmqF1IdrTehhWK67KWv_Jj6K16OtHrhD6dtbGHlpp5u-vOteq7HsOfjDngueiP1Y5DAPa-ohDIG3-ohqQOGhEpV43IH97QafKmo7g8Md02BK8DX9OSxTCCuO2kqo0fR-MYTDFgUs4rYsT-y-7GPhqyLXjLWyPN5uUpOT-frxBih3wYQmQzYbGUTgBi9pYzWthzIMs0W9dd400qKzqmt3hksax9Ixt9UmyuzDKkvTxxr_3yt5i52U0CyxEz7q1syQVdEd3N8nHJA_L8llyj709uTZwBR40snV_pnAO6UeIw-QODswdR39w4GpwnOis_vKkcmC27aQHre4OR2ClqI2LurPbUT5U4tCKZkbOQn3X-hZemU9FZXX7AgHWwwVYlvkhiaIsJgnFUYYTD56AkYj4dBelONklYZLRaPDg7zQT-2nq2BBjmmCaZqEHchr9-er3yfbDP6cP-xo)






`--binariesonly`
https://docs.thinkboxsoftware.com/products/deadline/10.3/1_User%20Manual/manual/deploy-client-centrally-managed.html
```
sudo /nfs/installers/Deadline-10.2.1.1-linux-installers/DeadlineClient-10.2.1.1-linux-x64-installer.run --nobinaries /data/share/nfs/test_data/10.2/opt/Thinkbox/Deadline10 --prefix /data/share/nfs/test_data/10.2/opt/Thinkbox/Deadline10
```

https://docs.thinkboxsoftware.com/products/deadline/10.3/1_User%20Manual/manual/deploy-client-centrally-managed.html#control-environment-variables
https://docs.thinkboxsoftware.com/products/deadline/10.3/1_User%20Manual/manual/deploy-client-centrally-managed.html#create-config-files


```
export DEADLINE_CONFIG_FILE=/home/michael/git/repos/deadline-docker/10.2/configs/Deadline10/deadline_client.ini
export DEADLINE_SYSTEM_PATH="${HOME}/.config/thinkbox/deadline/10.2/var/lib"
export DEADLINE_ROAMING_USER_PATH="${HOME}/.config/thinkbox/deadline/10.2"
/nfs/test_data/10.2/opt/Thinkbox/Deadline10/bin/deadlinelauncher
```

```
webservice-runner-10-2              | [2024-12-20 23:28:14] INFO:deadline_docker.deadline_wrapper_10_2.deadline_wrapper:WARNING: Ignoring HOME environment because effective user is root.
webservice-runner-10-2              | ERROR: UpdateClient.MaybeSendRequestNow caught an exception: POST http://rcs-runner-10-2.farm.evil:8888/rcs/v1/update returned "One or more errors occurred. (Name or service not known (rcs-runner-10-2.farm.evil:8888))" (Deadline.Net.Clients.Http.DeadlineHttpRequestException)
webservice-runner-10-2              | ERROR: DataController threw a configuration exception during initialization: Failed to establish connection to rcs-runner-10-2.farm.evil:8888 due to a communication error. (Deadline.Configuration.DeadlineConfigException)
webservice-runner-10-2              | Could not connect to Deadline Repository: Failed to establish connection to rcs-runner-10-2.farm.evil:8888 due to a communication error.
webservice-runner-10-2              | Deadline Web Service will try to connect again in 10 seconds...
webservice-runner-10-2              | Web Service Shutting Down...
webservice-runner-10-2              | 
webservice-runner-10-2              | [2024-12-20 23:28:14] ERROR:deadline_docker.deadline_wrapper_10_2.deadline_wrapper:

```