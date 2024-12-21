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

[./10.2/docker-compose.yaml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNrtWdtu4zYQ_RWB2yAvuvsSWw8FmmYLFEizi02wQBsFBiXRiRpZNEQ5cdbwvy91v5GSLCd-2heD0pw5M5wZDmlqB2zsIGCAs7Od67uhIezOwye0QueGcO7A4Pl8vz87M_2lh1_tJxiEwt2l6QvC95u_bj_f3H379-uXv2_uQkRCB4ZQU3W8Du-eXP_ZwtsrBB3P9dEVlViQIE1dYf8RR8DrL3_-cb3bmeC3HSVaxEyLmGqvRGSLCKRoqqwrlFDJGJUmpRJzKhF-EbOaYL8XtpIsHKApyNJWSJyz6Bzu06GkqZL-0Jwu2_HYMLXLltVMNEk5qovrm9s-6sNSMDxQaLsOECF5tKT0BS9mfSJTcA4PT43DSWdBlq6HrAC_EhSUho4V5VJWcphSEpbHsmPlhWWChiS2X3oZ27axv3QfOZb_J9hPbKcwruUIWbYtN4VM8-9RHgOqo9UNmi3m4knTyF1A5TS3GugosyG6bbbT3DnwkYQoILRBIucVB89kDW30BldeNcUpbpEAlRwpR9Bi-hmuAYh9SIUOernP-Oj4getP-tDpTfrI82UF6a8LPfcHDF3sky7nmMlPa7g1xm0UPP1jdPvabl9C39AaEzfEwZumHrGxlWk6drIyNHE-FQS5wPVJCD0PBVGbzsRSIZdywMC23W5y0BI7lLI9LUclozMFtcDbnov8kB30RNYd8P5VNqQ0mh4OTvkRVKx0c-jSXlUEPMPTw2q1mxUQJcPIFFTqZC8wUDzXYqWxplItRJsEG9-vLyKbSMnrYZlszV99QZc8OHXFtNvu2x6GkDCbQp2orT6OS_t649Fdvpn4-P3JUl_14tTJ77LeM_0DaVgFwKD6uBKITjgoYNRAIjhZEdT8OHUVdJrvWQZDeVh1wOL6wEJAFq26F9dmNYRCeLqCaPpz8qLo40LfwjiCi1kcbD7-UUOQpN97HDzZTaiizD7G9FCs72ys9wdYYk8iJqjeIrXE7ABzXdq82dWW8SEWWzTr1kr_2hkRqF0b8RDxEy1CKXu8V9KB8sCkKZCx3_k_y4akI2VsNKuIObyVCmJj6oXJRjVizoGxiqEKrUW0mPq9UoyTuFaSV8EywloTdkeWrcAJLoe9Hl82jBFiNpAVZQ6SE-gyOsLbHiR0W1wKL9jbrBCJYuoZn9TlZDxGIgkD_IyMT_poPp1ZOf5dLhDFKkn748eY6LwBFrsvaj_CUbpvdbneebsodl34HW5z4BHiHWkbZO_nRdsJ8ZePv3w8rY9ZO660aB-FWX8eLSeaNcn780y71K4ui_6c7qFi0e1jZdMHIlihYAVdBxhgFymYIP6mawKDDqOvuiYw_T3FwU2Ib998GxhhsEEiCPDm8QkYS0j3KhFs1nSa6MqFjwFcZZA19P_DOH9MMJ-dyIESBBg7sAXGhSrr2miszsf6aKbPNF0Eb8DQZro8uRjN1OnFVJ_OJ6O9CH7EnKo8m421qTYfz-fzyWQ-nogAxdz_JJ-p46_V-5-AvZqz)
[./10.2/docker-third-party/ayon/docker-compose.override.yml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNqNU8uO2yAU_RXEKEpHcozfwSyjdNlVqy4az4LYOLHGhgzgNKnlfy94xk4czWJW3MfhnANcOpiLgkECF4uu4pUmoFvqI2vYkoBlQeXrsu8Xi4yXtfibH6nU4Ncm4wD8ZjqvRU5rXTWs65BJ0ZT3PVi5YF4D7uoCTkLpg2Rq922Mnl8GtoJqqgw946Wy8Z4qpuhV8BH3VtuyEbILGqDIYNEERhaNbvChY4xcrJMzlaiu9o_tmSfrY4yN_RWQzKSVFvK6Q7cYDYYlKypzimF5fnmAW4Bi8szkJ42ZRCP4QRT7HfoI7sjv-w-EU9XW85oqtWUlOIu6bQxvWdU1efLKOIqYo7QUr4w8BWGa4P2Enz-f89XrHzVmupzpUTQsY38fT6LY3_jbzU30dhHOxxGGzRmHDmyYbGhVmEHs7IYMDkOYQWJCO4YZzHhvcLTV4ueV55Bo2TIHStEejpCUtFYma0_GJttW9CBpM0JOlP8RYkrfMd8La-QOAkkHL5CsPTfww8hLoyDEAfYDB14h8XHgxusQe8k6CZI0DnsH_hs4PRfjyE_8NPJ8vMZemjqQDdw_3v_V8L36__6bLI8)
[./10.2/docker-third-party/cgwire/docker-compose.kitsu.yaml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNp1Ustu2zAQ_BViA8MJoAf1NMVDD0V6DBCgRQ8tc2AkyhYskS5JpU4F_XspGXLspD1xZ2e4s9zlAKWqBFBYrYZGNpaiYW13ohNritYV1_v1OK5WTNat-l3uuLbo22cmEfp-UMZutTDL-astlayHgUEQLrnwjQwmlsE4Ij9ADEJhyws2jNKw4438eAEF_hHtG2v6CMc_58CPsB8_zU1U3HLjuhKyNsMQTjCccegSzuvozN5lrwp-KHK68S_ZI769zdIkvrtzL_A_XXATW7bcmHtRoxfV9p0wqG7alt7gOktT4Rmr1V7QmzgpcvJ81v9viN5VS9doMbgyPShtF8uMZ5tsc7Z8zsu4rt8sH_FJzSR40Antpl657Q-TgsG8eQbUhdPuGTA5Oh3vrfr6KkugVvfCA6367Q5ozVvjUH9wDYr7hm817xbJgcsfSp3hSfOlaqzSFxKgAxyBRiSIoyTNYxIXGSlImnrwOqVxkG0SgvNNHudFlowe_JmL4oCQNMqjAkc5jkiSJR6IufjD6TfPn3r8CyoD80E)






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