#!/usr/bin/env bash

# https://distribution.github.io/distribution/about/deploying/#run-an-externally-accessible-registry
# https://stackoverflow.com/a/10176685
# https://medium.com/@ifeanyiigili/how-to-setup-a-private-docker-registry-with-a-self-sign-certificate-43a7407a1613

# https://arminreiter.com/2022/01/create-your-own-certificate-authority-ca-using-openssl/

pushd /home/michael/git/repos/OpenStudioLandscapes/.registry
mkdir -p certs
# https://serverfault.com/a/666884
echo subjectAltName = DNS:localhost,IP:127.0.0.1,IP:192.168.1.165 > extfile.cnf
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -sha256 -days 365 -nodes -extfile extfile.cnf
# openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -sha256 -days 365 -nodes -addext "subjectAltName=DNS:localhost,IP:127.0.0.1,IP:192.168.1.165"
popd
