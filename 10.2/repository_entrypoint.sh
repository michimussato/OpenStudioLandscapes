#!/bin/bash

#if [ ! -f "/deadline_installer/Deadline-${DEADLINE_VERSION}-linux-installers.tar" ]; then
#  curl --progress-bar "https://www.googleapis.com/drive/v3/files/${GOOGLE_ID}?alt=media&key=${GOOGLE_API_KEY}" -o "/deadline_installer/Deadline-${DEADLINE_VERSION}-linux-installers.tar"
#fi;
#
#tar -xvf "/deadline_installer/Deadline-${DEADLINE_VERSION}-linux-installers.tar" "/deadline_installer/Deadline-${DEADLINE_VERSION}-linux-installers"

install_repository () {
    if [ ! -f "/opt/Thinkbox/DeadlineRepository10/settings/repository.ini" ]; then
        echo "Install Repository"
        /deadline_installer/Deadline-${DEADLINE_VERSION}-linux-installers/DeadlineRepository-${DEADLINE_VERSION}-linux-x64-installer.run \
        --mode unattended \
        --dbhost $DB_HOST \
        --dbport 27017 \
        --installmongodb false \
        --installSecretsManagement true \
        --secretsAdminName $SECRETS_USERNAME \
        --secretsAdminPassword $SECRETS_PASSWORD \
        --prefix /opt/Thinkbox/DeadlineRepository10 \
        --dbname deadline10db

#        echo "Install Custom Elements from https://github.com/postwork-io/custom.git"
#        git clone https://github.com/postwork-io/custom.git
#        rsync --ignore-existing -raz ./custom /repo

    else
        echo "Repository Already Installed"

    fi
}

## Todo: rsync
#rm -rf /opt/Thinkbox/DeadlineDatabase10/mongo/certificates/*
#cp -rv /opt/Thinkbox/DeadlineDatabase10/mongo/.certificates/* /opt/Thinkbox/DeadlineDatabase10/mongo/certificates

#top -b

python3 /usr/local/bin/docker-entrypoint.py mongod --config /opt/Thinkbox/DeadlineDatabase10/mongo/config.conf

#/opt/Thinkbox/DeadlineDatabase10/mongo/application/bin/mongod --config /opt/Thinkbox/DeadlineDatabase10/mongo/data/config.conf