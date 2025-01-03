FROM michimussato/base_image_10_2:latest AS client_image_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

ARG DEADLINE_VERSION
ARG RCS_HTTP_PORT_CONTAINER
ARG WEBSERVICE_HTTP_PORT_CONTAINER

WORKDIR /installers

RUN deadline-wrapper-10-2  \
    -vv  \
    install-client  \
    --installer /installers/DeadlineClient.run  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/Deadline10"  \
    --repositorydir "/opt/Thinkbox/DeadlineRepository10"  \
    --httpport ${RCS_HTTP_PORT_CONTAINER}  \
    --webservice-httpport ${WEBSERVICE_HTTP_PORT_CONTAINER}

WORKDIR /opt/Thinkbox

ENTRYPOINT []
