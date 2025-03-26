#!/usr/bin/env bash


# TOC
# max-concurrent-uploads:
# # Limit concurrent uploads:
# # - https://stackoverflow.com/a/48348339
# features:
# # https://docs.docker.com/build/buildkit/#getting-started


sudo bash -c 'cat > /usr/lib/systemd/system/openstudiolandscapes-registry.service << EOF
# https://www.baeldung.com/linux/systemd-services-environment-variables
[Unit]
Description=OpenStudioLandscapes Docker Registry Service
Documentation=
Requires=docker.service

[Service]
Type=simple
EnvironmentFile=/home/michael/git/repos/OpenStudioLandscapes/.registry/registry.env
WorkingDirectory=/home/michael/git/repos/OpenStudioLandscapes/.registry
ExecStart=/usr/bin/docker container run --env \${ENV_REGISTRY_HTTP_ADDR} --env \${ENV_REGISTRY_HTTP_TLS_CERTIFICATE} --env \${ENV_REGISTRY_HTTP_TLS_KEY} --domainname \${DOMAIN_NAME} --hostname \${HOST_NAME} --name \${CONTAINER_NAME} --rm --publish \${PUBLISH} --volume \${DAEMON_JSON} --volume \${REGISTRY_ROOT} --volume \${CERTS_ROOT} \${REGISTRY}
ExecReload=/bin/kill -HUP \${MAINPID}

[Install]
WantedBy=multi-user.target

EOF'

sudo systemctl daemon-reload
sudo systemctl enable openstudiolandscapes-registry.service
sudo systemctl restart openstudiolandscapes-registry.service
sudo journalctl -fu openstudiolandscapes-registry.service
