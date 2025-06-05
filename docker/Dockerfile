# Build:
# docker build --tag docker.io/michimussato/openstudiolandscapes:0.3 --tag docker.io/michimussato/openstudiolandscapes:latest --no-cache-filter=openstudiolandscapes-never-cache . --build-arg PYTHON_MAJ=3 --build-arg PYTHON_MIN=11 --build-arg PYTHON_PAT=11 --build-arg DOCKER_GID=$(getent group docker | cut -d: -f3)
#
# Push:
# docker login
# docker image push --all-tags michimussato/openstudiolandscapes
#
# Run:
# docker run -v /var/run/docker.sock:/var/run/docker.sock:rw --rm -it --entrypoint bash michimussato/openstudiolandscapes:latest


FROM ubuntu:22.04 AS openstudiolandscapes
LABEL authors="michael"

ARG PYTHON_MAJ
ARG PYTHON_MIN
ARG PYTHON_PAT
ARG DOCKER_GID

ENV PYTHON_EXE=python$PYTHON_MAJ.$PYTHON_MIN
ENV PIP_EXE=pip$PYTHON_MAJ.$PYTHON_MIN
ENV PYTHON_VERSION=$PYTHON_MAJ.$PYTHON_MIN.$PYTHON_PAT

ARG DEBIAN_FRONTEND=noninteractive
ENV CONTAINER_TIMEZONE=Europe/Zurich
ENV SET_CONTAINER_TIMEZONE=true

SHELL ["/bin/bash", "-c"]

USER root

RUN echo "Installing Dependencies to get Python:"
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends  \
    curl  \
    file  \
    ca-certificates

RUN echo "Installing Dependencies to build Python:"
RUN apt-get install -y --no-install-recommends  \
    build-essential  \
    pkg-config  \
    zlib1g-dev  \
    libncurses5-dev  \
    libgdbm-dev  \
    libnss3-dev  \
    libssl-dev  \
    libreadline-dev  \
    libffi-dev  \
    libsqlite3-dev  \
    libbz2-dev  \
    iproute2  \
    liblzma-dev

RUN echo "Installing Additional Dependencies:"
RUN apt-get install -y --no-install-recommends  \
    ssh  \
    git  \
    htop  \
    vim  \
    graphviz
# RUN apt-get clean

# Clone Repo
# Pull if Repo already cloned
# RUN git clone --tags git@github.com:michimussato/OpenStudioLandscapes.git
#RUN git -C OpenStudioLandscapes pull

RUN echo "Building Python $PYTHON_VERSION:"
WORKDIR /build/python

RUN curl "https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz" -o Python-$PYTHON_VERSION.tgz
RUN file Python-$PYTHON_VERSION.tgz
RUN tar -xvf Python-$PYTHON_VERSION.tgz

RUN cd Python-$PYTHON_VERSION && ./configure --enable-optimizations  # Todo: --prefix  # https://stackoverflow.com/questions/11307465/destdir-and-prefix-of-make
RUN cd Python-$PYTHON_VERSION && make -j $(nproc)
RUN cd Python-$PYTHON_VERSION && make altinstall  # altinstall instead of install because the later command will overwrite the default system python3 binary.

RUN $PYTHON_EXE -m pip install --upgrade pip setuptools setuptools_scm wheel

# RUN thinkbox-ssl-gen --help

RUN rm -rf /build/python

RUN apt-get clean

# Todo:
#  - [ ] gid depends on the docker gid on the host. maybe via ARG?
RUN groupadd --force --gid $DOCKER_GID docker
RUN useradd --create-home --shell /bin/bash openstudiolandscapes
RUN usermod --append --groups docker openstudiolandscapes

RUN echo "Installing Docker:"
COPY ./ubuntu_2204__script_install_docker.sh .
RUN chmod +x ubuntu_2204__script_install_docker.sh
RUN ./ubuntu_2204__script_install_docker.sh

USER openstudiolandscapes

ENV REPOS_DIR=/home/openstudiolandscapes/git/repos
WORKDIR $REPOS_DIR

# Always clone even if Docker Build Cache is enabled
# https://github.com/moby/moby/issues/1996#issuecomment-1763467972
FROM openstudiolandscapes AS openstudiolandscapes-never-cache
RUN echo "Cloning OpenStudioLandscapes:"
# Clone Repo
# Pull if Repo already cloned
RUN git clone --verbose --tags https://github.com/michimussato/OpenStudioLandscapes.git
# RUN git -C OpenStudioLandscapes pull
WORKDIR $REPOS_DIR/OpenStudioLandscapes

RUN echo "Creating virtualenv:"
# https://pythonspeed.com/articles/activate-virtualenv-dockerfile/
ENV VIRTUAL_ENV=$REPOS_DIR/OpenStudioLandscapes/.venv
RUN $PYTHON_EXE -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN echo "Installing OpenStudioLandscapes:"
RUN $PIP_EXE --verbose install -e .[dev]

# Nox: use HTTPS instead of SSH?
# 0.582 root > cmd = ['/usr/bin/git', '-C', PosixPath('/home/openstudiolandscapes/git/repos/OpenStudioLandscapes/.features'), 'clone', '--tags', '--branch', 'main', '--single-branch', 'git@github.com:michimussato/OpenStudioLandscapes-Ayon.git']
# 0.582 nox > /usr/bin/git -C /home/openstudiolandscapes/git/repos/OpenStudioLandscapes/.features clone --tags --branch main --single-branch git@github.com:michimussato/OpenStudioLandscapes-Ayon.git
# 0.583 Cloning into 'OpenStudioLandscapes-Ayon'...
# 1.065 Host key verification failed.
# 1.066 fatal: Could not read from remote repository.
# 1.066
# 1.066 Please make sure you have the correct access rights
# 1.066 and the repository exists.

WORKDIR $REPOS_DIR/OpenStudioLandscapes/.features

# Add Features here...
# RUN git clone --verbose --tags https://github.com/michimussato/OpenStudioLandscapes-Ayon.git
RUN git clone --verbose --tags https://github.com/michimussato/OpenStudioLandscapes-Dagster.git
RUN $PIP_EXE --verbose install -e ./OpenStudioLandscapes-Dagster[dev]
# RUN git clone --verbose --tags https://github.com/michimussato/OpenStudioLandscapes-Kitsu.git

ENV DAGSTER_HOME=$REPOS_DIR/OpenStudioLandscapes/.dagster-postgres
WORKDIR $DAGSTER_HOME

WORKDIR $REPOS_DIR/OpenStudioLandscapes

ENTRYPOINT []
