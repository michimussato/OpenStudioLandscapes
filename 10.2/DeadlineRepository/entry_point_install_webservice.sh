#!/bin/bash


#if [ ! -d /deadline_installer ]; then
#    echo "Directory /deadline_installer not found.";
#    exit 1;
#fi;


#if [ ! -f /deadline_installer/DeadlineClient-${DEADLINE_VERSION}-linux-x64-installer.run ]; then
#    echo "DeadlineClient installer not found.";
#    exit 1;
#fi;


#rm -f /tmp/installbuilder_installer.log || true
#
#
#if [ "${FORCE_REINSTALL}" == "true" ]; then
#    echo "Force-removing DeadlineRepository...";
#    rm -rf /opt/Thinkbox/DeadlineRepository10/* || true
#fi;
#
#
#if [ -f /opt/Thinkbox/DeadlineRepository10/settings/repository.ini ]; then
#    echo "Previous version of DeadlineRepository ${DEADLINE_VERSION} found.";
#    exit 1;
#fi;


if [ "$1" = "install" ]; then
    echo "Installing DeadlineClient (webservice_config)...";

    ./DeadlineClient-${DEADLINE_VERSION}-linux-x64-installer.run \
    --mode unattended \
    --prefix /opt/Thinkbox/Deadline10 \
    --repositorydir /opt/Thinkbox/DeadlineRepository10 \
    --launcherdaemon false \
    --enable-components webservice_config \
    --blockautoupdateoverride NotBlocked \
    --webserviceuser root \
    --webservice_httpport 8899 \
    --webservice_enabletls false

    mv -f /tmp/installbuilder_installer.log /opt/Thinkbox/Deadline10
    cat /opt/Thinkbox/Deadline10/installbuilder_installer.log

    exit 0;
fi;
