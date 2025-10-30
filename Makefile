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

# Todo:
#  - [ ] deprecate OPENSTUDIOLANDSCAPES__REPO_ROOT (replace by OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT)
#ifdef OPENSTUDIOLANDSCAPES__REPO_ROOT
#OPENSTUDIOLANDSCAPES__REPO_ROOT := $(OPENSTUDIOLANDSCAPES__REPO_ROOT)
#else
OPENSTUDIOLANDSCAPES__REPO_ROOT := $(shell pwd)
#endif

#ifdef OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT
#OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT := $(OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT)
#else
OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT := $(shell pwd)
#endif

#ifdef OPENSTUDIOLANDSCAPES__DOMAIN_LAN
#OPENSTUDIOLANDSCAPES__DOMAIN_LAN := $(OPENSTUDIOLANDSCAPES__DOMAIN_LAN)
#else
#OPENSTUDIOLANDSCAPES__DOMAIN_LAN := openstudiolandscapes.lan
#endif

#ifdef OPENSTUDIOLANDSCAPES__HARBOR_USERNAME
#OPENSTUDIOLANDSCAPES__HARBOR_USERNAME := $(OPENSTUDIOLANDSCAPES__HARBOR_USERNAME)
#else
#OPENSTUDIOLANDSCAPES__HARBOR_USERNAME := admin
#endif

#ifdef OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD
#OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD := $(OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD)
#else
#OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD := Harbor12345
#endif

export OPENSTUDIOLANDSCAPES_VERSION_TAG=v1.6.0-rc1

# REPLACED := $(shell echo ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} | sed 's/\//\\\//g')

#ifdef OPENSTUDIOLANDSCAPES_VERSION_TAG
#OPENSTUDIOLANDSCAPES_VERSION_TAG := $(OPENSTUDIOLANDSCAPES_VERSION_TAG)
#else
#OPENSTUDIOLANDSCAPES_VERSION_TAG := v1.6.0-rc1
#endif

#install: \
#		disable_unattended \
#		install_deps \
#		install_gh_cli \
#		install_python \
#		install_docker \
#		edit_hosts_file \
#		harbor_prepare \
#		harbor_up \
#		harbor_init_projects

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
	# failed: Connection timed out.
	# failed: Connection timed out.
	# failed: Connection timed out.
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

#	sudo -s << EOF
#	mkdir -p /etc/docker
#	touch /etc/docker/daemon.json
#	cat > /etc/docker/daemon.json
#	{
#		"features": {
#		"buildkit": true
#	},
#		"max-concurrent-uploads": 1,
#		"insecure-registries" : [
#			"http://harbor.farm.evil:80",
#			"http://192.168.1.162:5000",
#			"http://192.168.1.163:5000",
#			"http://192.168.1.164:80",
#			"http://192.168.1.165:80",
#			"http://127.0.0.1:5000",
#			"http://localhost:5000",
#			"http://10.1.2.15:5000",
#			"http://[::1]:5000"
#		]
#	}
#	EOF

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

#	sudo systemctl daemon-reload
#	# sudo systemctl restart docker
#
#	sudo git config --global --add safe.directory ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}
#	sudo git -C ${REPODIR} clean -d -x --force ${REPODIR}/.landscapes/.harbor
#
#	echo "Your /etc/docker/daemon.json file looks like:
#	cat /etc/docker/daemon.json

#install_openstudiolandscapes:
#	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}
#	source .venv/bin/activate
#	pip install --upgrade pip setuptools setuptools_scm wheel
#	pip install -e .[dev]
#	nox -s clone_features
#	nox -s install_features_into_engine
#	deactivate

edit_hosts_file:
	for fqdn in \
		dagster.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
		postgres-dagster.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
		harbor.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
		pi-hole.${OPENSTUDIOLANDSCAPES__DOMAIN_LAN} \
	; do \
		sudo sed -i -e "\$$a127.0.0.1    $$fqdn" -e "/127.0.0.1    $${fqdn}/d" /etc/hosts; \
	done

	echo "Your /etc/hosts file looks like:"
	cat /etc/hosts

# git clone --tags https://github.com/michimussato/OpenStudioLandscapes.git
# git checkout -B <branch> origin/<branch>
openstudiolandscapes_install:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& python3.11 -m venv .venv \
		&& source .venv/bin/activate \
		&& pip install --upgrade pip setuptools setuptools_scm wheel \
		&& pip install -e .[dev] \
		&& deactivate

openstudiolandscapes_features_clone:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& nox -s clone_features \
		&& deactivate

openstudiolandscapes_features_install:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& nox -s install_features_into_engine \
		&& deactivate

harbor_prepare:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& source ./.env \
		&& openstudiolandscapesutil-harborcli --user $${OPENSTUDIOLANDSCAPES__HARBOR_USERNAME} --password $${OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD} --host $${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME} --port $${OPENSTUDIOLANDSCAPES__HARBOR_PORT} --harbor-root-dir $${OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR} prepare download \
		&& openstudiolandscapesutil-harborcli --user $${OPENSTUDIOLANDSCAPES__HARBOR_USERNAME} --password $${OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD} --host $${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME} --port $${OPENSTUDIOLANDSCAPES__HARBOR_PORT} --harbor-root-dir $${OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR} prepare extract --tar-file ./.harbor/download/harbor-*.tgz \
		&& openstudiolandscapesutil-harborcli --user $${OPENSTUDIOLANDSCAPES__HARBOR_USERNAME} --password $${OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD} --host $${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME} --port $${OPENSTUDIOLANDSCAPES__HARBOR_PORT} --harbor-root-dir $${OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR} prepare configure \
		&& openstudiolandscapesutil-harborcli --user $${OPENSTUDIOLANDSCAPES__HARBOR_USERNAME} --password $${OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD} --host $${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME} --port $${OPENSTUDIOLANDSCAPES__HARBOR_PORT} --harbor-root-dir $${OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR} prepare install \
		&& deactivate

harbor_up:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& source ./.env \
		&& eval $$(openstudiolandscapesutil-harborcli --user $${OPENSTUDIOLANDSCAPES__HARBOR_USERNAME} --password $${OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD} --host $${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME} --port $${OPENSTUDIOLANDSCAPES__HARBOR_PORT} --harbor-root-dir $${OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR} systemd install --enable --start --su-method sudo) \
		&& deactivate

	sudo systemctl status --no-pager --full harbor.service

harbor_log:
	journalctl --follow --unit harbor.service

harbor_init_projects:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& source ./.env \
		&& openstudiolandscapesutil-harborcli --user $${OPENSTUDIOLANDSCAPES__HARBOR_USERNAME} --password $${OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD} --host $${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME} --port $${OPENSTUDIOLANDSCAPES__HARBOR_PORT} --harbor-root-dir $${OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR} project create --project-name openstudiolandscapes \
		&& openstudiolandscapesutil-harborcli --user $${OPENSTUDIOLANDSCAPES__HARBOR_USERNAME} --password $${OPENSTUDIOLANDSCAPES__HARBOR_PASSWORD} --host $${OPENSTUDIOLANDSCAPES__HARBOR_HOSTNAME} --port $${OPENSTUDIOLANDSCAPES__HARBOR_PORT} --harbor-root-dir $${OPENSTUDIOLANDSCAPES__HARBOR_ROOT_DIR} project delete --project-name library \
		&& deactivate

nox_CLEAR_ALL:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.nox \
		&& rm -r */
		# && sudo rm -r */

harbor_git_clean:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.harbor \
		&& sudo git clean -x --force ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.harbor

harbor_CLEAR_ALL:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT}/.harbor \
		&& sudo pwd \
		&& sudo rm -r */

setup_venv:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& python3.11 -m venv .venv


openstudiolandscapes_update:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
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
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& nox --sessions dagster_postgres_up_detach dagster_postgres \
		&& deactivate

down:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& nox --sessions dagster_postgres_down \
		&& deactivate

restart: down up

#teleport_prepare:
#	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
#		&& source .venv/bin/activate \
#		&& openstudiolandscapesutil-teleportcli Todo \
#		&& openstudiolandscapesutil-teleportcli Todo \
#		&& openstudiolandscapesutil-teleportcli Todo \
#		&& openstudiolandscapesutil-teleportcli Todo \
#		&& deactivate

teleport_local_node_install:
	# https://goteleport.com/download/client-tools/
	curl https://cdn.teleport.dev/install.sh | bash -s 18.2.6

teleport_local_node_login:
	# export TELEPORT_FQDN=teleport.openstudiolandscapes.cloud-ip.cc
	tsh login --proxy=$${TELEPORT_FQDN} --user=admin

teleport_local_node_create_token:
	mkdir -p $${HOME}/.config/teleport
	tctl tokens add --type=node --format=text > $${HOME}/.config/teleport/teleport-node_token

teleport_local_node_configure:
	teleport node configure \
    	--data-dir=$${HOME}/.local/share/teleport \
    	--output=file://$${HOME}/.config/teleport/teleport-node.yaml \
    	--token=$${HOME}/.config/teleport/teleport-node_token \
    	--proxy=${TELEPORT_FQDN}:443

define teleport_node_service
sudo bash -c 'cat << EOF > /usr/lib/systemd/user/teleport-node@.service
[Unit]
Description=Teleport Node Service (%i)
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=5
# EnvironmentFile has to be absolute, so the following
# will not work (hence, disabled):
# EnvironmentFile=-\${HOME}/.config/teleport/teleport
ExecStart=$(which teleport) start --config %h/.config/teleport/teleport-node.yaml --pid-file=\${HOME}/teleport/teleport-node.pid
# systemd before 239 needs an absolute path
ExecReload=/bin/sh -c "exec pkill -HUP -L -F %h/.local/share/teleport/teleport-node.pid"
PIDFile=%h/teleport/teleport-node.pid
LimitNOFILE=524288

[Install]
# Todo:
#  ::Unit \${HOME}/.config/systemd/user/teleport.service is added as a dependency to a non-existent unit multi-user.target.
# WantedBy=multi-user.target
WantedBy=default.target
EOF' && echo "Install successful"
endef
export script = $(value teleport_node_service)

teleport_local_node_install_unit:
	# the PID file needs its directory to exist:
	#mkdir -p $${HOME}/teleport
	@ eval "$$script"

teleport_local_node_enable_unit:
	systemctl --user daemon-reload
	systemctl --user enable --now teleport-node@$${USER}.service
	systemctl --user status --no-pager --full teleport-node@$${USER}.service

teleport_local_node_uninstall_unit:
	systemctl --user disable --now teleport-node@$${USER}.service
	systemctl --user status --no-pager --full teleport-node@$${USER}.service
	#systemctl --user daemon-reload
	sudo rm /usr/lib/systemd/user/teleport-node@.service
	sudo systemctl daemon-reload

teleport_local_node_journal:
	journalctl --user --follow --unit teleport-node@$${USER}.service

nox:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& nox

nox_readme:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& nox --sessions readme

nox_tag:
	cd ${OPENSTUDIOLANDSCAPES__REPOSITORY_ROOT} \
		&& source .venv/bin/activate \
		&& nox --sessions tag


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
##
##	if command -v "docker/"; then;\
##		if docker ps | grep "goharbor/"; then;\
##			echo "Docker Container Harbor is running!";\
##			echo "It is not advisable to perform this installation while Harbor is running.";\
##			echo;\
##			echo "Stop the containers and re-run the installer.";\
##			echo "Run `docker stop $(docker ps -q)` to stop all running containers.";\
##			echo;\
##			exit 1;\
##		fi
##	fi

help:
	# https://stackoverflow.com/a/26339924
	@LC_ALL=C $(MAKE) -pRrq -f $(firstword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/(^|\n)# Files(\n|$$)/,/(^|\n)# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'
