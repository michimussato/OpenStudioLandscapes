<!-- TOC -->
* [`deadline.ini`](#deadlineini)
* [Ports](#ports)
* [Deadline Docker 10.2](#deadline-docker-102)
  * [Symlinks](#symlinks)
  * [Automated](#automated)
<!-- TOC -->

---

# `deadline.ini`

https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/manual/client-config.html#client-config-conn-server-ref-label

# Ports

https://docs.thinkboxsoftware.com/products/deadline/10.2/1_User%20Manual/manual/considerations.html#firewall-anti-virus-security-considerations

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

[./10.2/docker-compose.yaml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNrtWdtu2zgQ_RWB3SAvuvoi1XpYYLNpgQJpWjTBArtRYFAS7aiRRYOSE6eG_32p-426WHb81BeD0hyeGc4cDWVqByxsI6CDi4ud4zmBzu0ugye0Qpc6d2lD8ny5319cGN7Cxa_WEyQBd39leBz3z-3nu0-39z_-_f7ty-19gPzAhgFU5BFeB_dPjvds4u01grbreOiaWkzoI0VeYW-JQ-DNt7__utntDPDHjhLNI6Z5RLWXQrJ5CJIUWRxJlFBKGaU6pRRxSiF-HrEaYL_ntoLIHTCTE4UtFwdn0jU8JENBkYXRY3257MAjx9Qv21ZxUSdtmDq_ub3rM31YCYYnCm3XBPl-li0hudGUsz6ZyTmHp6fCYSer8BeOi0yCX31ECkPbDGspShlMKhiLY9E2M2EZoGaJ_BduRr4t7C2cZYPnnz72Yt8JrNFziCz6FutGpvtTyGOAOlrD6FDBkLlFBTRUwIZLP0DEp_0L2a-YPPtraKE3uHLLFUhw8xgoZUgxhOaPd4qrAaIYEqONXh5SPjp-bIwnueiMJrlsimUF6a8DXecXDBzs-V3BMfK7bS_OkLnF4rTNb5fnD7TGvhNg8qbIR2waRZqOXaIIjYNPDCQzOJ4fQNdFJGyBqVnI7UIGGNgS210Oej4OpWwvy1HF6CxBJfGW6yAvYCc9tnUnvL_KhkijHuHgkh9BxSp3A13SaPKEp3j6IlhuRTlESjEiBRXa0AskkuuYrDJWppSFaPlk43nVh8jyhfj2sEq21q_6QBciOLdi2n33bQ9DSJhNoUrUpo_jyr7euHSLrhc-un-20pejOHfxu7z3LP9AGpYAGFTvJ4Hw9QQRhgZiw9lEUInj3CrodN9TBkN5WDpgcb2jEJBJVffiWKyGkBvPJ4h6PGcXRZ8Q-grjCC6mONh8za8anCD82ePFk92ESpPZrzE9JlZ3Ntb9AzyxFxERlE9oWnJ2gLuu2U2rqzzGh3hsmVn1VvjLzchA5UimCRFdUREK6eWDlAykRyZNjozizv5Z1iwdJWOjWSJu4C0piI2pCpONquW8AcYSQxlayWi-9AcpH8d5LRWvhGWktWLszix7QkNyG9ir-WXDGClmA1lZbkA2JLqIDvGWC326LS64F-xuVsgPc-rqH-TFdDJBvB8Q_Iz0D6PxTP1oZviTHM7xZZL2y_dx0Xm6yncfgp4l0M6DQL7rbO6E2S7u-yekrZGdLoq2t7_fMf6O8bwxpq221H49FKS9d7yYKuY0670flSvl-irvvcn-yOedPJpseIAHK0RW0LGBDnbhBANE30INoNNh-DXUAIa3pzi4CfDdm2cBPSAbxAOCN8snoC8g3Yd4sFnTZaJrBy4JXKWQNfT-wzi7jDGf7DCAAgToO7AFuqCpmjjSlJk2UqfqaMqDN3pzPFZFVdFUZaJNVHk21qZ7HvyKSDVRHaljeTababKiyOqEByji_hp_3o2-8u7_BzFzXB8)
[./10.2/docker-third-party/ayon/docker-compose.override.yml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNqNU11vmzAU_SuWuyirRCB8mYTHKJ20h2XTGk3aQlUZMAmqsTPjpMks_vuMW0iI9rAn7se555yLbQUznhMYw9FIlayUMVBjuSMVGcdgnGPxMm6a0ShhBeWv2Q4LCdaLhAHwg8iM8gxTWVZEKUenTp83DZjYYFgD9uQE9ryWW0Hqzccuun8ybKtPjw-r9fef375-Xq1zLHGKa1LjM2cd8Ddty0ol8IPS6GcDfzb4xuknnHbEucyYTgK1oVPr6IiFQ8v0FjDw1vrpYr3GBAii01Jycd44l9gxxgXJS72N-dw_3cBbQE3EkYh_NAYSFWdbnqcb5z24Ir_u3xD21baeUVzXS1KAI6eHSvMWJaXx3bQIg4BYtRT8hcR3nj9Hs7THD4_R-u9j6EQGwozITtUvQjcNe9WZu3CXi4vq5U9Y7zuY4YRBC1ZEVLjM9Y1U7UACzW1MYKzD9j4mMGGNxuGD5I9nlsFYigOxoOCH7Q7GBaa1zg57bZMsS7wVuOoge8x-cd6nb5iHvDVyBYGxgicYTyIU2V7kziMPhcgLLXjWRd9HNnIj5AZRgKZzPwobC_4xpJGNPOS7U38W-kEQRp4FieH-8vbAzDtr_gJuRSv-)
[./10.2/docker-third-party/cgwire/docker-compose.kitsu.yaml](https://mermaid-js.github.io/mermaid-live-editor/view#pako:eNp1Ul1v0zAU_SuWR9VNyqcT28QPPKANCQlKRSskwKjyEqeNmsbFcUZHlP9O4ipdy7Yn-55z7j3-OC1MVSYhg5NJW1SFYaCdmo3cySkD00zo7bTrJhNe5aX6k26ENmD5nlcAfNur2qy1rMf1d5mqKm9bDj1_xPwn0htYDrsOuB7g0JcmPWP9MPZ3oqieNwDPPYBtYeomDNBPu3HDwEW_7CFmHxZ3s-XX7_MvH2fLwftN20Mri60s2FnPgzV9ibyY_3zma52rT7PFS93z4PoaxxG6uenv6b474wY2LUVd38ocPKiy2cka5EVZsqsgx3EsndpotZXsCkUJeXt_0r_21M7lSf8rR4sL273SZjTFAlNMT6b3JEV5_mQ6D45qXkEH7qTufyfrU9IOCg5tQjhk_XbICIe86nqdaIxaPFYpZEY30oFaNesNZLko675q9pkw8rYQay12o2Qvqh9Kncqj5i4rjNJnEshaeIDMpYR6iIYJRQQThB342INRRDwSUhLGNCZBElHcOfCvHUo9gkgUJDjBCIU4RA6UdvbnY-ht9rt_TyT4nQ)






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