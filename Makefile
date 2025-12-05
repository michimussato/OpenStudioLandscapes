# env
# OPENSTUDIOLANDSCAPES__REPO_ROOT=~/git/repos/OpenStudioLandscapes
# VERSION_TAG=v1.6.0-rc1

-include .env

SHELL := $(shell which bash)

ifdef PYTHON_MAJ
PYTHON_MAJ := $(PYTHON_MAJ)
else
PYTHON_MAJ := 3
endif

ifdef PYTHON_MIN
PYTHON_MIN := $(PYTHON_MIN)
else
PYTHON_MIN := 11
endif

ifdef PYTHON_PAT
PYTHON_PAT := $(PYTHON_PAT)
else
PYTHON_PAT := 11
endif


#install: \
#		disable_unattended \
#		install_deps \
#		install_gh_cli \
#		install_python \
#		install_docker \
#		edit_hosts_file

disable_unattended:
	echo "Starting prep..."
	sudo systemctl disable --now unattended-upgrades

install_deps:
	sudo apt-get update
	sudo apt-get -y autoremove
	sudo apt-get -y upgrade
	sudo apt-get install --no-install-recommends -y \
		openssh-server \
		git \
		htop \
		vim \
		graphviz
	sudo apt-get clean
	sudo systemctl enable --now ssh

install_gh_cli:
	# https://github.com/cli/cli/blob/trunk/docs/install_linux.md#debian
	(type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
		&& sudo mkdir -p -m 755 /etc/apt/keyrings \
		&& out=$$(mktemp) && wget -nv -O$$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
		&& cat $$out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
		&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
		&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
		&& echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
		&& sudo apt update \
		&& sudo apt install gh -y

	gh --version

# Ref
# (type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
#	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
#	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
#	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
#	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
#	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
#	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
#	&& sudo apt update \
#	&& sudo apt install gh -y
#
# Actual
# (type -p wget >/dev/null || (sudo apt update && sudo apt install wget -y)) \
#	&& sudo mkdir -p -m 755 /etc/apt/keyrings \
#	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
#	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
#	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
#	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
#	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
#	&& sudo apt update \
#	&& sudo apt install gh -y

install_python:
	sudo apt-get install --no-install-recommends -y \
		build-essential \
		zlib1g-dev \
		libncurses5-dev \
		libgdbm-dev \
		libnss3-dev \
		libssl-dev \
		libreadline-dev \
		libffi-dev \
		pkg-config \
		liblzma-dev \
		libbz2-dev \
		libsqlite3-dev \
		curl

	cd "$$(mktemp -d)" || exit 1 && \
		curl "https://www.python.org/ftp/python/${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}/Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz" -o Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz \
		&& tar -xvf Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT}.tgz \
		&& cd Python-${PYTHON_MAJ}.${PYTHON_MIN}.${PYTHON_PAT} || exit 1 \
		&& ./configure --enable-optimizations \
		&& make -j "$$(nproc)" \
		&& sudo make altinstall \
	# popd || exit 1

install_docker:
	# https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
	# sudo groupadd --force --gid 959 docker
	# sudo usermod --append --groups docker $${USER}

	# https://docs.docker.com/engine/install/ubuntu/
	for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do \
		sudo apt-get remove $$pkg ; \
	done

	sudo apt autoremove -y
	sudo apt-get update
	sudo apt-get install --no-install-recommends -y \
		ca-certificates \
		curl

	sudo install -m 0755 -d /etc/apt/keyrings
	sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
	sudo chmod a+r /etc/apt/keyrings/docker.asc

	echo \
		"deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
		$$(. /etc/os-release && echo "$${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
		sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
	sudo apt-get update
	sudo apt-get install --no-install-recommends -y \
		docker-ce \
		docker-ce-cli \
		containerd.io \
		docker-buildx-plugin \
		docker-compose-plugin

	sudo systemctl status --no-pager --full docker.service
	sudo systemctl status --no-pager --full containerd.service

	# sudo systemctl enable --now docker.service
	# sudo systemctl enable --now containerd.service

edit_hosts_file:
	for fqdn in \
		openstudiolandscapes-dagster.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
		openstudiolandscapes-dagster-postgres.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
	; do \
		sudo sed -i -e "\$$a127.0.0.1    $$fqdn" -e "/127.0.0.1    $${fqdn}/d" /etc/hosts; \
	done

	echo "Your /etc/hosts file looks like:"
	cat /etc/hosts

# git clone --tags https://github.com/michimussato/OpenStudioLandscapes.git
# git checkout -B <branch> origin/<branch>
# or
# git clone --tags --branch <branch> https://github.com/michimussato/OpenStudioLandscapes.git
openstudiolandscapes_install:
	python3.11 -m venv .venv \
		&& source .venv/bin/activate \
		&& pip install --upgrade pip setuptools setuptools_scm wheel \
		&& pip install -e .[dev] \
		&& deactivate

openstudiolandscapes_features_clone:
	source .venv/bin/activate \
		&& nox -s clone_features \
		&& deactivate

openstudiolandscapes_features_install:
	source .venv/bin/activate \
		&& nox -s install_features_into_engine \
		&& deactivate

###############################################################################


###############################################################################
# CLEAN UP

#nox_CLEAR_ALL:
#	rm -r ./.nox/*/

setup_venv:
	python3.11 -m venv .venv

openstudiolandscapes_update:
	source .venv/bin/activate \
		&& pip install -e .[dev] \
		&& deactivate

#add_aliases:
#	# Escape dots
#	# Working syntax:
#	# sed -i -e '$asource /home/user/git/repos/OpenStudioLandscapes/\.openstudiolandscapesrc' -e '/source \/home\/user\/git\/repos\/OpenStudioLandscapes\/\.openstudiolandscapesrc/d' /home/user/.bashrc
#	# $ echo "your/string" | sed 's/\//\\\//g'
#	# your\/string
#	sed -i -e '$$asource ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/\.openstudiolandscapesrc' -e '/source ${REPLACED}\/\.openstudiolandscapesrc/d' "$${HOME}/.bashrc"

up:
	source .venv/bin/activate \
		&& nox --sessions dagster_postgres_up_detach dagster_postgres \
		&& deactivate

down:
	source .venv/bin/activate \
		&& nox --sessions dagster_postgres_down \
		&& deactivate

###############################################################################

###############################################################################
# NOX

nox:
	source .venv/bin/activate \
		&& nox

nox_readme:
	source .venv/bin/activate \
		&& nox --sessions readme

nox_tag:
	source .venv/bin/activate \
		&& nox --sessions tag

nox_checkout:
	source .venv/bin/activate \
		&& nox --sessions checkout_branch

###############################################################################

#reboot:
#	read -r -e -p "Reboot now? " choice_reboot
#	[[ "$choice_reboot" == [Yy]* ]] \
#		&& sudo systemctl reboot \
#		|| echo "Ok, let\'s reboot later."

#initial_checks:
##	#$ make initial_checks
##	#mkdir -p /home/user/git/repos/OpenStudioLandscapes || sudo mkdir -p /home/user/git/repos/OpenStudioLandscapes
##	#if [  -eq 0 ]; then
##	#/bin/sh: 1: Syntax error: end of file unexpected (expecting "fi")
##	#make: *** [Makefile:216: initial_checks] Error 2
##	mkdir -p ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}
##	# sudo mkdir -p ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}
#
#	UID := $(shell id -u)
#	ifeq ($(UID),0)
#		echo "Operation not permitted."
#		echo
#		echo "This OpenStudioLandscapes installer must not be executed as user root!"
#		echo "Re-run as regular user."
#		echo
#		exit 1
#	endif
#
##	if ! groups $$USER | grep -qw "docker"; then;\
##		sudo groupadd --force --gid 959 docker || exit 1;\
##		sudo usermod --append --groups docker "$${USER}" || exit 1;\
##		echo "User $$USER has been added to group \`docker\`.";\
##		echo "Reboot now and re-run this scrip.";\
##	fi

help:
	# https://stackoverflow.com/a/26339924
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'
