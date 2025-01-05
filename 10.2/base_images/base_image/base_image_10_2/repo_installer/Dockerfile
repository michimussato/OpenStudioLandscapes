FROM michimussato/base_image_10_2:latest AS repository_image_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

ARG DEADLINE_VERSION
ARG MONGO_DB_PORT_HOST
ARG MONGO_DB_NAME
ARG MONGO_DB_HOST

WORKDIR /installers

RUN deadline-wrapper-10-2  \
    -vv  \
    install-repository  \
    --installer /installers/DeadlineRepository.run  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/DeadlineRepository10"  \
    --dbtype "MongoDB"  \
    --dbhost ${MONGO_DB_HOST}  \
    --dbport ${MONGO_DB_PORT_HOST}  \
    --dbname ${MONGO_DB_NAME}

WORKDIR /opt/Thinkbox

ENTRYPOINT []