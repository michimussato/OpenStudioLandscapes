#!/usr/bin/env bash


pushd /home/michael/git/repos/OpenStudioLandscapes/.registry


# Step 1: Create a private key for the CA

CANAME=OpenStudioLandscapes-RootCA

# optional
mkdir $CANAME
cd $CANAME

# generate aes encrypted private key
openssl genrsa -aes256 -out $CANAME.key 4096


# Step 2: Create Certificate of the CA

# create certificate, 1826 days = 5 years
# the following will ask for common name, country, ...
# openssl req -x509 -new -nodes -key $CANAME.key -sha256 -days 1826 -out $CANAME.crt

# ... or you provide common name, country etc. via:
openssl req -x509 -new -nodes -key $CANAME.key -sha256 -days 1826 -out $CANAME.crt -subj '/CN=OpenStudioLandscapes Root CA/C=CH/ST=Zurich/L=Zurich/O=OpenStudioLandscapes'


# Step 3: Add the CA certificate to the trusted root certificates

# https://wiki.archlinux.org/title/User:Grawity/Adding_a_trusted_CA_certificate
sudo trust anchor --store $CANAME.crt
# or:
# sudo cp $CANAME.crt /etc/ca-certificates/trust-source/anchors
# sudo update-ca-trust


# Step 4: Create a certificate for the webserver

MYCERT=openstudiolandscapes-registry
openssl req -new -nodes -out $MYCERT.csr -newkey rsa:4096 -keyout $MYCERT.key -subj '/CN=OpenStudioLandscapes Registry/C=CH/ST=Zurich/L=Zurich/O=OpenStudioLandscapes'

# create a v3 ext file for SAN properties
cat > $MYCERT.v3.ext << EOF
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = myserver.local
DNS.3 = myserver1.local
IP.1 = 127.0.0.1
IP.2 = 192.168.1.1
IP.3 = 192.168.2.1
IP.3 = 192.168.1.165
IP.4 = 172.17.0.1
EOF


# Step 5: Sign the certificate

openssl x509 -req -in $MYCERT.csr -CA $CANAME.crt -CAkey $CANAME.key -CAcreateserial -out $MYCERT.crt -days 730 -sha256 -extfile $MYCERT.v3.ext


# End

# /usr/bin/docker exec --interactive --tty <container_id> sh
# update-ca-certificates
# /usr/bin/docker exec --interactive --tty <container_id> update-ca-certificates

popd
