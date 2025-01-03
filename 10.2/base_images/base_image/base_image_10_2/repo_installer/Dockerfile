FROM michimussato/base_image_10_2:latest AS repository_image_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

ARG DEADLINE_VERSION
ARG MONGO_DB_PORT_HOST

WORKDIR /installers

RUN deadline-wrapper-10-2  \
    -vv  \
    install-repository  \
    --installer /installers/DeadlineRepository.run  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/DeadlineRepository10"  \
    --dbtype "MongoDB"  \
    --dbhost "mongodb-10-2"  \
    --dbport ${MONGO_DB_PORT_HOST}  \
    --dbname "deadline10db"

WORKDIR /opt/Thinkbox

ENTRYPOINT []