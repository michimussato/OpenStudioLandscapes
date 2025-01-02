FROM michimussato/base_image_10_2:latest AS repo_installer_10_2
LABEL authors="michimussato@gmail.com"

SHELL ["/bin/bash", "-c"]

ARG DEADLINE_VERSION
ARG INSTALLERS_ROOT

ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV INSTALLERS_ROOT=$INSTALLERS_ROOT

WORKDIR /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    install-repository  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/DeadlineRepository10"  \
    --dbtype "MongoDB"  \
    --dbhost "mongodb-10-2"  \
    --dbport 27017  \
    --dbname "deadline10db"
