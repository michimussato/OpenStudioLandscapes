#!/bin/bash



if [ ! -d /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers ]; then
    echo "Directory /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers not found.";
    exit 1;
fi;


if [ ! -f /nfs/installers/Deadline-${DEADLINE_VERSION}-linux-installers/DeadlineRepository-${DEADLINE_VERSION}-linux-x64-installer.run ]; then
    echo "DeadlineRepository installer not found.";
    exit 1;
fi;


rm -f /tmp/installbuilder_installer.log || true


if [ "${FORCE_REINSTALL}" == "true" ]; then
    echo "Force-removing DeadlineRepository...";
    rm -rf /opt/Thinkbox/DeadlineRepository10/* || true
fi;


if [ -f /opt/Thinkbox/DeadlineRepository10/settings/repository.ini ]; then
    echo "Previous version of DeadlineRepository ${DEADLINE_VERSION} found.";
    exit 1;
fi;


if [ "$1" = "install" ]; then
    echo "Installing DeadlineRepository...";

    ./DeadlineRepository-${DEADLINE_VERSION}-linux-x64-installer.run \
        --mode unattended \
        --prefix /opt/Thinkbox/DeadlineRepository10 \
        --setpermissions true \
        --dbtype MongoDB \
        --installmongodb false \
        --dbhost mongodb-10-2 \
        --dbport 27017 \
        --dbname deadline10db \
        --dbauth false \
        --dbssl false \
        --installSecretsManagement false \
        --importrepositorysettings false


    mv -f /tmp/installbuilder_installer.log /opt/Thinkbox/DeadlineRepository10
    cat /opt/Thinkbox/DeadlineRepository10/installbuilder_installer.log

    exit 0;
fi;
