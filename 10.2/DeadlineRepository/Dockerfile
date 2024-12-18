FROM ubuntu:20.04 AS repo_base
LABEL authors="michael"

ARG DEADLINE_VERSION
ARG PYTHON_VERSION
ARG FORCE_REINSTALL
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION
ENV FORCE_REINSTALL=$FORCE_REINSTALL

#ARG DEADLINE_VERSION
#ARG PYTHON_VERSION
#
#ENV DEADLINE_VERSION=$DEADLINE_VERSION
#ENV PYTHON_VERSION=$PYTHON_VERSION

#ENV DEADLINE_VERSION=$DEADLINE_VERSION
#ENV PYTHON_VERSION=$PYTHON_VERSION

RUN apt-get update \
    && apt-get upgrade -y

RUN apt-get install \
    -y \
    --no-install-recommends \
    git \
    ca-certificates \
    file  \
    curl

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
# RUN thinkbox-ssl-gen --help

RUN rm -rf /build/python

RUN apt-get clean

ENTRYPOINT []



FROM repo_base AS repo_installer
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

LABEL authors="michael"

WORKDIR /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers

ENTRYPOINT ["top","-b"]
#ENTRYPOINT  \
    deadline-wrapper  \
    -vv  \
    --force-reinstall  \
    install-repository  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/DeadlineRepository10"  \
    --dbtype "MongoDB"  \
    --dbhost "mongodb-10-2"  \
    --dbport 27017  \
    --dbname "deadline10db"



FROM repo_base AS rcs_installer
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

LABEL authors="michael"

WORKDIR /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers

# deadline-wrapper --force-reinstall install-rcs --deadline-version 10.2.1.1 --prefix /opt/Thinkbox/Deadline10 --repositorydir /opt/Thinkbox/DeadlineRepository10 --httpport 8888
ENTRYPOINT  \
    deadline-wrapper  \
    -vv  \
    --force-reinstall  \
    install-rcs  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/Deadline10"  \
    --repositorydir "/opt/Thinkbox/DeadlineRepository10"  \
    --httpport 8888




FROM rcs_installer AS rcs_runner
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

LABEL authors="michael"

WORKDIR /ENTRYPOINT

ADD ./DeadlineRepository/entry_point_rcs_runner.sh /ENTRYPOINT
RUN chmod u+x /ENTRYPOINT/entry_point_rcs_runner.sh

WORKDIR /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers

ENTRYPOINT [  \
    "/ENTRYPOINT/entry_point_rcs_runner.sh"  \
]



FROM repo_base AS webservice_installer
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

LABEL authors="michael"

WORKDIR /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers

ENTRYPOINT  \
    deadline-wrapper  \
    -vv  \
    --force-reinstall  \
    install-webservice  \
    --deadline-version ${DEADLINE_VERSION}  \
    --prefix "/opt/Thinkbox/Deadline10"  \
    --repositorydir "/opt/Thinkbox/DeadlineRepository10"  \
    --webservice-httpport 8899



FROM webservice_installer AS webservice_runner
ARG DEADLINE_VERSION
ARG PYTHON_VERSION
#
ENV DEADLINE_VERSION=$DEADLINE_VERSION
ENV PYTHON_VERSION=$PYTHON_VERSION

LABEL authors="michael"

WORKDIR /ENTRYPOINT

ADD ./DeadlineRepository/entry_point_webservice_runner.sh /ENTRYPOINT
RUN chmod u+x /ENTRYPOINT/entry_point_webservice_runner.sh

WORKDIR /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers

ENTRYPOINT [  \
    "/ENTRYPOINT/entry_point_webservice_runner.sh"  \
]
