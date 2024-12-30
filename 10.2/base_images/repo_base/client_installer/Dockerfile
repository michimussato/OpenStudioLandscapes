FROM michimussato/repo_base:latest AS client_installer
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
    install-client  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/Deadline10"  \
    --repositorydir "/opt/Thinkbox/DeadlineRepository10"  \
    --httpport 8888  \
    --webservice-httpport 8899
