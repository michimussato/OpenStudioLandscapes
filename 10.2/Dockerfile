FROM ubuntu:20.04 AS repo_base
LABEL authors="michael"

ARG DEBIAN_FRONTEND=noninteractive

ARG DEADLINE_VERSION
ARG PYTHON_VERSION

ENV CONTAINER_TIMEZONE="Australia/Sydney"
ENV SET_CONTAINER_TIMEZONE=true

ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

RUN apt-get update \
    && apt-get upgrade -y

RUN apt-get install \
    -y \
    --no-install-recommends \
    git \
    ca-certificates \
    file  \
    tzdata  \
    curl  \
    ffmpeg  \
    xvfb  \
    libegl1  \
    libsm6  \
    libglu1-mesa  \
    libxss1

WORKDIR /build/python

RUN apt-get install -y --no-install-recommends make build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev
RUN curl https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz -o Python-${PYTHON_VERSION}.tgz
RUN file Python-${PYTHON_VERSION}.tgz
RUN tar -xvf Python-${PYTHON_VERSION}.tgz

RUN cd Python-${PYTHON_VERSION} && ./configure --enable-optimizations  # Todo: --prefix  # https://stackoverflow.com/questions/11307465/destdir-and-prefix-of-make
RUN cd Python-${PYTHON_VERSION} && make -j $(nproc)
RUN cd Python-${PYTHON_VERSION} && make altinstall  # altinstall instead of install because the later command will overwrite the default system python3 binary.

RUN python3.11 -m pip install pip --upgrade

RUN python3.11 -m pip install --root-user-action=ignore git+https://github.com/michimussato/SSLGeneration.git@packaging
RUN python3.11 -m pip install --root-user-action=ignore git+https://github.com/michimussato/DeadlineWrapper.git@main
RUN python3.11 -m pip install --root-user-action=ignore "deadline-dagster @ git+https://github.com/michimussato/deadline-dagster.git@main"
RUN python3.11 -m pip install --root-user-action=ignore "dagster-shared @ git+https://github.com/michimussato/dagster-shared.git@main"
# RUN thinkbox-ssl-gen --help

RUN rm -rf /build/python

RUN apt-get clean

ENTRYPOINT []



FROM repo_base AS likec4_dev

LABEL authors="michael"

WORKDIR /git

RUN git -C /git clone https://github.com/likec4/likec4.git
RUN git -C /git clone https://github.com/asdf-vm/asdf.git --branch v0.15.0

RUN source /git/asdf/asdf.sh
RUN source /git/asdf/completions/asdf.bash

WORKDIR /git/asdf

RUN asdf plugin add nodejs
RUN asdf plugin add yarn
RUN asdf plugin add dprint

RUN asdf install

WORKDIR /git/likec4

RUN yarn install
RUN yarn build

WORKDIR /git/likec4/apps/playground

ENTRYPOINT yarn dev --host 0.0.0.0 --port 4567




FROM repo_base AS dagster_dev
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

LABEL authors="michael"

RUN python3.11 -m pip install --root-user-action=ignore "dagster-shared[dagster_dev] @ git+https://github.com/michimussato/dagster-shared.git@main"

WORKDIR /dagster/materializations
ENV DAGSTER_HOME="/dagster/materializations"

ENTRYPOINT dagster dev --workspace "/dagster/workspace.yaml" --port 3000 --host 0.0.0.0



FROM repo_base AS repo_installer
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

#ARG INSTALLERS_ROOT
ENV INSTALLERS_ROOT=$INSTALLERS_ROOT

LABEL authors="michael"

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



FROM repo_base AS client_installer
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

# ARG INSTALLERS_ROOT
ENV INSTALLERS_ROOT=$INSTALLERS_ROOT

LABEL authors="michael"

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



FROM client_installer AS rcs_runner

LABEL authors="michael"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlinercs"



FROM client_installer AS pulse_runner

LABEL authors="michael"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlinepulse"  \
    --arguments "['-nogui', '-nosplash']"



FROM client_installer AS worker_runner

LABEL authors="michael"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlineworker"  \
    --arguments "['-nogui', '-nosplash']"



FROM client_installer AS webservice_runner

LABEL authors="michael"

ENTRYPOINT  \
    deadline-wrapper-10-2  \
    -vv  \
    run  \
    --executable "/opt/Thinkbox/Deadline10/bin/deadlinewebservice"
