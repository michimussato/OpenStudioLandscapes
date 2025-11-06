<!-- TOC -->
* [acme.sh](#acmesh)
  * [Certificate CA](#certificate-ca)
    * [`letsencrypt`](#letsencrypt)
      * [nox](#nox)
        * [`acme-sh-openstudiolandscapes-cloud-ip-cc`](#acme-sh-openstudiolandscapes-cloud-ip-cc)
    * [`letsencrypt_test`](#letsencrypt_test)
      * [nox](#nox-1)
        * [`acme-sh-openstudiolandscapes-cloud-ip-cc.openstudiolandscapes.lan`](#acme-sh-openstudiolandscapes-cloud-ip-ccopenstudiolandscapeslan)
        * [`acme-sh-openstudiolandscapes-cloud-ip-cc.farm.evil`](#acme-sh-openstudiolandscapes-cloud-ip-ccfarmevil)
        * [`acme-sh-openstudiolandscapes-cloud-ip-cc`](#acme-sh-openstudiolandscapes-cloud-ip-cc-1)
  * [File Structure](#file-structure)
    * [acme.sh](#acmesh-1)
    * [Caddy](#caddy)
<!-- TOC -->

---

> [!NOTE]
> The current way of creating certificates using Let's Encrypt
> is by using the pre-configured `nox` sessions. It would be preferable, 
> however, to have `caddy` manage the validity of certificates. This though, to date,
> is not working yet because the files generated differ from the structure currenly
> expected ([see structure](#file-structure)).

# acme.sh

## Certificate CA

### `letsencrypt`

#### nox

##### `acme-sh-openstudiolandscapes-cloud-ip-cc`

```
$ nox -s acme_sh_prepare acme_sh_up_detach acme_sh_register_account acme_sh_create_certificate acme_sh_down
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
Using temporary directory: /tmp/tmp6tluttc9
nox > Running session acme_sh_prepare
nox > Creating virtual environment (virtualenv) using python in /tmp/tmp6tluttc9/acme_sh_prepare

Description:

Certificate CA:
1) letsencrypt
2) letsencrypt_test
3) buypass
4) buypass_test
5) zerossl
6) sslcom
7) google
8) googletest
9) Manual
Choice: 1

Description:

Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
2) Manual
Choice: 1
Email account:
michimussato@gmail.com
ClouDNS Auth ID: 44124
ClouDNS Auth Password: helloworld
root > Contents Pi-hole docker-compose.yml: 
services:                                                                                                                                                                                                          
  acme-sh-openstudiolandscapes-cloud-ip-cc:                                                                                                                                                                        
    command:                                                                                                                                                                                                       
    - daemon                                                                                                                                                                                                       
    container_name: acme-sh-openstudiolandscapes-cloud-ip-cc                                                                                                                                                       
    domainname: openstudiolandscapes.lan                                                                                                                                                                           
    environment:                                                                                                                                                                                                   
      ACME_SH_CA: letsencrypt                                                                                                                                                                                      
      ACME_SH_CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                             
      ACME_SH_CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                    
      ACME_SH_EMAIL: michimussato@gmail.com                                                                                                                                                                        
      ACME_SH_TLD: openstudiolandscapes.cloud-ip.cc                                                                                                                                                                
      CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                                     
      CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                            
    hostname: acme-sh-openstudiolandscapes-cloud-ip-cc                                                                                                                                                             
    image: docker.io/neilpang/acme.sh                                                                                                                                                                              
    network_mode: host                                                                                                                                                                                             
    restart: always                                                                                                                                                                                                
    stdin_open: true                                                                                                                                                                                               
    tty: true                                                                                                                                                                                                      
    volumes:                                                                                                                                                                                                       
    - /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs:/acme.sh:rw                                                                                         
                                                                                                                                                                                                                   
root > docker-compose.yml created: 
/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml                                                                                              
nox > Session acme_sh_prepare was successful in 40 seconds.
nox > Running session acme_sh_up_detach
nox > Creating virtual environment (virtualenv) using python in /tmp/tmp6tluttc9/acme_sh_up_detach

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'up', '--remove-orphans', '--detach']                                                                                                 
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc up --remove-orphans --detach                                                                                                                                          
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Creating
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Created
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Starting
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Started
nox > Session acme_sh_up_detach was successful in 2 seconds.
nox > Running session acme_sh_register_account
nox > Creating virtual environment (virtualenv) using python in /tmp/tmp6tluttc9/acme_sh_register_account

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
nox > container_env = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'acme-sh-openstudiolandscapes-cloud-ip-cc', 'ACME_SH_TLD': 'openstudiolandscapes.cloud-ip.cc', 'CLOUDNS_AUTH_ID': '44124', 'CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_CA': 'letsencrypt', 'ACME_SH_CLOUDNS_AUTH_ID': '44124', 'ACME_SH_CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_EMAIL': 'michimussato@gmail.com', 'LE_CONFIG_HOME': '/acme.sh', 'AUTO_UPGRADE': '1', 'HOME': '/root'}                                                                                                                                              
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --register-account --server $ACME_SH_CA --email $ACME_SH_EMAIL'
[Mon Nov  3 12:32:25 UTC 2025] Account key creation OK.
[Mon Nov  3 12:32:25 UTC 2025] Registering account: https://acme-v02.api.letsencrypt.org/directory
[Mon Nov  3 12:32:26 UTC 2025] Registered
[Mon Nov  3 12:32:26 UTC 2025] ACCOUNT_THUMBPRINT='mB_rCm7aP8FuErB5LJ7JHKCv2g8emIhyikRuVLRU7y0'
nox > Session acme_sh_register_account was successful in 3 seconds.
nox > Running session acme_sh_create_certificate
nox > Creating virtual environment (virtualenv) using python in /tmp/tmp6tluttc9/acme_sh_create_certificate

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
nox > container_env = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'acme-sh-openstudiolandscapes-cloud-ip-cc', 'ACME_SH_TLD': 'openstudiolandscapes.cloud-ip.cc', 'CLOUDNS_AUTH_ID': '44124', 'CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_CA': 'letsencrypt', 'ACME_SH_CLOUDNS_AUTH_ID': '44124', 'ACME_SH_CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_EMAIL': 'michimussato@gmail.com', 'LE_CONFIG_HOME': '/acme.sh', 'AUTO_UPGRADE': '1', 'HOME': '/root'}                                                                                                                                              
Sub-Domains (comma-separated):
Top Level Domain: openstudiolandscapes.cloud-ip.cc
Sub-Domains: teleport.,*.teleport.
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --issue --server $ACME_SH_CA --force --dns dns_cloudns --domain openstudiolandscapes.cloud-ip.cc --domain teleport.openstudiolandscapes.cloud-ip.cc --domain *.teleport.openstudiolandscapes.cloud-ip.cc'                                                                                                                                          
[Mon Nov  3 12:32:41 UTC 2025] Using CA: https://acme-v02.api.letsencrypt.org/directory
[Mon Nov  3 12:32:41 UTC 2025] Creating domain key
[Mon Nov  3 12:32:41 UTC 2025] The domain key is here: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.key
[Mon Nov  3 12:32:41 UTC 2025] Multi domain='DNS:openstudiolandscapes.cloud-ip.cc,DNS:teleport.openstudiolandscapes.cloud-ip.cc,DNS:*.teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 12:32:46 UTC 2025] Getting webroot for domain='openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 12:32:46 UTC 2025] Getting webroot for domain='teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 12:32:46 UTC 2025] Getting webroot for domain='*.teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 12:32:46 UTC 2025] Adding TXT value: 3Qg9VQ3jaPRRlDbz1U6HJOTMx3q2M5M_9ZBh2jcATXY for domain: _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:32:46 UTC 2025] Using cloudns
[Mon Nov  3 12:32:48 UTC 2025] Adding the TXT record for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:32:50 UTC 2025] Added.
[Mon Nov  3 12:32:50 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 12:32:50 UTC 2025] Adding TXT value: n92e_jyfsTgMISSz-F-1d7JAa_mpsZ4qjOJCH6eNPUM for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:32:50 UTC 2025] Using cloudns
[Mon Nov  3 12:32:52 UTC 2025] Adding the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:32:52 UTC 2025] Added.
[Mon Nov  3 12:32:52 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 12:32:52 UTC 2025] Adding TXT value: 21XoohtgyFba0cctvbqNH69VE1zyRAOLQv2qVV4Tbi0 for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:32:52 UTC 2025] Using cloudns
[Mon Nov  3 12:32:57 UTC 2025] Adding the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:32:57 UTC 2025] Added.
[Mon Nov  3 12:32:57 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 12:32:57 UTC 2025] Let's check each DNS record now. Sleeping for 20 seconds first.
[Mon Nov  3 12:33:17 UTC 2025] You can use '--dnssleep' to disable public dns checks.
[Mon Nov  3 12:33:17 UTC 2025] See: https://github.com/acmesh-official/acme.sh/wiki/dnscheck
[Mon Nov  3 12:33:17 UTC 2025] Checking openstudiolandscapes.cloud-ip.cc for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:17 UTC 2025] Success for domain openstudiolandscapes.cloud-ip.cc '_acme-challenge.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 12:33:17 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:17 UTC 2025] Success for domain teleport.openstudiolandscapes.cloud-ip.cc '_acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 12:33:17 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:19 UTC 2025] Success for domain teleport.openstudiolandscapes.cloud-ip.cc '_acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 12:33:19 UTC 2025] All checks succeeded
[Mon Nov  3 12:33:19 UTC 2025] Verifying: openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:20 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 12:33:23 UTC 2025] Success
[Mon Nov  3 12:33:23 UTC 2025] Verifying: teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:24 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 12:33:26 UTC 2025] Success
[Mon Nov  3 12:33:26 UTC 2025] Verifying: *.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:29 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 12:33:32 UTC 2025] Success
[Mon Nov  3 12:33:32 UTC 2025] Removing DNS records.
[Mon Nov  3 12:33:32 UTC 2025] Removing txt: 3Qg9VQ3jaPRRlDbz1U6HJOTMx3q2M5M_9ZBh2jcATXY for domain: _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:32 UTC 2025] Using cloudns
[Mon Nov  3 12:33:36 UTC 2025] Deleting the TXT record for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:36 UTC 2025] Deleted.
[Mon Nov  3 12:33:36 UTC 2025] Successfully removed
[Mon Nov  3 12:33:36 UTC 2025] Removing txt: n92e_jyfsTgMISSz-F-1d7JAa_mpsZ4qjOJCH6eNPUM for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:36 UTC 2025] Using cloudns
[Mon Nov  3 12:33:42 UTC 2025] Deleting the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:42 UTC 2025] Deleted.
[Mon Nov  3 12:33:42 UTC 2025] Successfully removed
[Mon Nov  3 12:33:42 UTC 2025] Removing txt: 21XoohtgyFba0cctvbqNH69VE1zyRAOLQv2qVV4Tbi0 for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:42 UTC 2025] Using cloudns
[Mon Nov  3 12:33:47 UTC 2025] Deleting the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 12:33:49 UTC 2025] Deleted.
[Mon Nov  3 12:33:49 UTC 2025] Successfully removed
[Mon Nov  3 12:33:49 UTC 2025] Verification finished, beginning signing.
[Mon Nov  3 12:33:49 UTC 2025] Let's finalize the order.
[Mon Nov  3 12:33:49 UTC 2025] Le_OrderFinalize='https://acme-v02.api.letsencrypt.org/acme/finalize/2771984731/444533045721'
[Mon Nov  3 12:33:52 UTC 2025] Downloading cert.
[Mon Nov  3 12:33:52 UTC 2025] Le_LinkCert='https://acme-v02.api.letsencrypt.org/acme/cert/06e3c0a5fb67735ffd8e31626745791b069c'
[Mon Nov  3 12:33:53 UTC 2025] Cert success.
-----BEGIN CERTIFICATE-----
MIIEBzCCA42gAwIBAgISBuPApftnc1/9jjFiZ0V5GwacMAoGCCqGSM49BAMDMDIx
CzAJBgNVBAYTAlVTMRYwFAYDVQQKEw1MZXQncyBFbmNyeXB0MQswCQYDVQQDEwJF
ODAeFw0yNTExMDMxMTM1MTlaFw0yNjAyMDExMTM1MThaMCsxKTAnBgNVBAMTIG9w
ZW5zdHVkaW9sYW5kc2NhcGVzLmNsb3VkLWlwLmNjMFkwEwYHKoZIzj0CAQYIKoZI
zj0DAQcDQgAECA5t6o04nvWtAfXDnU8SCSIx5XAqxMnahNsy6AYuB8a7Bfzhk0hO
iZuUXRDbSF6STIUAf8AvPKNs9zMzrpUVzKOCAogwggKEMA4GA1UdDwEB/wQEAwIH
gDAdBgNVHSUEFjAUBggrBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADAd
BgNVHQ4EFgQUvYFizzjFtN8Y11gfqpBSh4S0Z70wHwYDVR0jBBgwFoAUjw0TovYu
ftFQbDMYOF1ZjiNykcowMgYIKwYBBQUHAQEEJjAkMCIGCCsGAQUFBzAChhZodHRw
Oi8vZTguaS5sZW5jci5vcmcvMIGDBgNVHREEfDB6gisqLnRlbGVwb3J0Lm9wZW5z
dHVkaW9sYW5kc2NhcGVzLmNsb3VkLWlwLmNjgiBvcGVuc3R1ZGlvbGFuZHNjYXBl
cy5jbG91ZC1pcC5jY4IpdGVsZXBvcnQub3BlbnN0dWRpb2xhbmRzY2FwZXMuY2xv
dWQtaXAuY2MwEwYDVR0gBAwwCjAIBgZngQwBAgEwLQYDVR0fBCYwJDAioCCgHoYc
aHR0cDovL2U4LmMubGVuY3Iub3JnLzI5LmNybDCCAQUGCisGAQQB1nkCBAIEgfYE
gfMA8QB3AGQRxGykEuyniRyiAi4AvKtPKAfUHjUnq+r+1QPJfc3wAAABmkm1m8IA
AAQDAEgwRgIhAL5nioYtrNGGz3FSETsJcmbObFd0ubYyM4HHBoYuUJFYAiEA663Y
+c+nFp6a0rPKGhgE8tZdwA1EEo5/gtHAmDIEWnwAdgAZhtTHKKpv/roDb3gqTQGR
qs4tcjEPrs5dcEEtJUzH1AAAAZpJtaOUAAAEAwBHMEUCIQCgxQuHzlzq8vuPF5gG
exh4zalmRgG3k0jjNi8MShFwAAIgCcgsdjDK1SBtYn4BXJj6kaVbX5S8R5EoUD8C
gB+axzQwCgYIKoZIzj0EAwMDaAAwZQIwXky7iK8/5Ws8kJvSXbHL0GPdTEDVcevH
IpLtkopm+TWQiaWZZQuQDuwV1pKPQq3WAjEAm7zQWDBU5Snwwz4f8KgJb/KdmTt0
3wCGRuXP5SGlnJuA6lkXEEtwulPNFdAR8UeB
-----END CERTIFICATE-----
[Mon Nov  3 12:33:53 UTC 2025] Your cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.cer
[Mon Nov  3 12:33:53 UTC 2025] Your cert key is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.key
[Mon Nov  3 12:33:53 UTC 2025] The intermediate CA cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/ca.cer
[Mon Nov  3 12:33:53 UTC 2025] And the full-chain cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/fullchain.cer
nox > Session acme_sh_create_certificate was successful in a minute.
nox > Running session acme_sh_down
nox > Creating virtual environment (virtualenv) using python in /tmp/tmp6tluttc9/acme_sh_down

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'down']                                                                                                                               
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc down                                                                                                                                                                  
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopping
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopped
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removing
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removed
nox > Session acme_sh_down was successful in 2 seconds.
nox > Ran 5 sessions in 2 minutes:
nox > * acme_sh_prepare: success, took 40 seconds
nox > * acme_sh_up_detach: success, took 2 seconds
nox > * acme_sh_register_account: success, took 3 seconds
nox > * acme_sh_create_certificate: success, took a minute
nox > * acme_sh_down: success, took 2 seconds
```

### `letsencrypt_test`

```shell
nox -s acme_sh_prepare acme_sh_up_detach acme_sh_register_account acme_sh_create_certificate acme_sh_down
```

#### nox

Issues:

`noxfile.write_acme_sh_yml()`

Refers to:
`.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml`

| `hostname`                                                                                                                              | Valid |
|-----------------------------------------------------------------------------------------------------------------------------------------|-------|
| [`acme-sh-openstudiolandscapes-cloud-ip-cc.openstudiolandscapes.lan`](#acme-sh-openstudiolandscapes-cloud-ip-ccopenstudiolandscapeslan) | ❌     |
| [`acme-sh-openstudiolandscapes-cloud-ip-cc.farm.evil`](#acme-sh-openstudiolandscapes-cloud-ip-ccfarmevil)                               | ✅     |
| [`acme-sh-openstudiolandscapes-cloud-ip-cc`](#acme-sh-openstudiolandscapes-cloud-ip-cc)                                                 | ✅     |


##### `acme-sh-openstudiolandscapes-cloud-ip-cc.openstudiolandscapes.lan`

```
$ nox -s acme_sh_prepare acme_sh_up_detach acme_sh_register_account acme_sh_create_certificate acme_sh_down
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
Using temporary directory: /tmp/tmpygwx5g02
nox > Running session acme_sh_prepare
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpygwx5g02/acme_sh_prepare

Description:

Certificate CA:
1) letsencrypt
2) letsencrypt_test
3) buypass
4) buypass_test
5) zerossl
6) sslcom
7) google
8) googletest
9) Manual
Choice: 2

Description:

Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
2) Manual
Choice: 1
Email account:
michimussato@gmail.com
ClouDNS Auth ID: 44124
ClouDNS Auth Password: helloworld
root > Contents Pi-hole docker-compose.yml: 
services:                                                                                                                                                                                                          
  acme-sh-openstudiolandscapes-cloud-ip-cc:                                                                                                                                                                        
    command:                                                                                                                                                                                                       
    - daemon                                                                                                                                                                                                       
    container_name: acme-sh-openstudiolandscapes-cloud-ip-cc                                                                                                                                                       
    domainname: openstudiolandscapes.lan                                                                                                                                                                           
    environment:                                                                                                                                                                                                   
      ACME_SH_CA: letsencrypt_test                                                                                                                                                                                 
      ACME_SH_CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                             
      ACME_SH_CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                    
      ACME_SH_EMAIL: michimussato@gmail.com                                                                                                                                                                        
      ACME_SH_TLD: openstudiolandscapes.cloud-ip.cc                                                                                                                                                                
      CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                                     
      CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                            
    hostname: acme-sh-openstudiolandscapes-cloud-ip-cc.openstudiolandscapes.lan                                                                                                                                    
    image: docker.io/neilpang/acme.sh                                                                                                                                                                              
    network_mode: host                                                                                                                                                                                             
    restart: always                                                                                                                                                                                                
    stdin_open: true                                                                                                                                                                                               
    tty: true                                                                                                                                                                                                      
    volumes:                                                                                                                                                                                                       
    - /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs:/acme.sh:rw                                                                                         
                                                                                                                                                                                                                   
root > docker-compose.yml created: 
/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml                                                                                              
nox > Session acme_sh_prepare was successful in 15 seconds.
nox > Running session acme_sh_up_detach
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpygwx5g02/acme_sh_up_detach

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'up', '--remove-orphans', '--detach']                                                                                                 
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc up --remove-orphans --detach                                                                                                                                          
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Creating
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Created
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Starting
Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: sethostname: invalid argument
nox > Command /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc up --remove-orphans --detach failed with exit code 1                                                                                                          
nox > Session acme_sh_up_detach failed.
nox > Running session acme_sh_register_account
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpygwx5g02/acme_sh_register_account

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
Error response from daemon: container 816c2f957211b383b2daf0267a3cefe7d668603098e607739656511b2db618df is not running
nox > container_env = {}
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --register-account --server $ACME_SH_CA --email $ACME_SH_EMAIL'
Error response from daemon: container 816c2f957211b383b2daf0267a3cefe7d668603098e607739656511b2db618df is not running
nox > Command bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --register-account --server $ACME_SH_CA --email $ACME_SH_EMAIL' failed with exit code 1
nox > Session acme_sh_register_account failed.
nox > Running session acme_sh_create_certificate
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpygwx5g02/acme_sh_create_certificate

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
Error response from daemon: container 816c2f957211b383b2daf0267a3cefe7d668603098e607739656511b2db618df is not running
nox > container_env = {}
Sub-Domains (comma-separated):
Top Level Domain: openstudiolandscapes.cloud-ip.cc
Sub-Domains: teleport.,*.teleport.
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --issue --server $ACME_SH_CA --force --dns dns_cloudns --domain openstudiolandscapes.cloud-ip.cc --domain teleport.openstudiolandscapes.cloud-ip.cc --domain *.teleport.openstudiolandscapes.cloud-ip.cc'                                                                                                                                          
Error response from daemon: container 816c2f957211b383b2daf0267a3cefe7d668603098e607739656511b2db618df is not running
nox > Command bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --issue --server $ACME_SH_CA --force --dns dns_cloudns --domain openstudiolandscapes.cloud-ip.cc --domain teleport.openstudiolandscapes.cloud-ip.cc --domain *.teleport.openstudiolandscapes.cloud-ip.cc' failed with exit code 1                                                                                                          
nox > Session acme_sh_create_certificate failed.
nox > Running session acme_sh_down
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpygwx5g02/acme_sh_down

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'down']                                                                                                                               
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc down                                                                                                                                                                  
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopping
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopped
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removing
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removed
nox > Session acme_sh_down was successful in a second.
nox > Ran 5 sessions in 48 seconds:
nox > * acme_sh_prepare: success, took 15 seconds
nox > * acme_sh_up_detach: failed, took a second
nox > * acme_sh_register_account: failed, took 11 seconds
nox > * acme_sh_create_certificate: failed, took 18 seconds
nox > * acme_sh_down: success, took a second
```

##### `acme-sh-openstudiolandscapes-cloud-ip-cc.farm.evil`

```
$ nox -s acme_sh_prepare acme_sh_up_detach acme_sh_register_account acme_sh_create_certificate acme_sh_down
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
Using temporary directory: /tmp/tmpsoi1npqk
nox > Running session acme_sh_prepare
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpsoi1npqk/acme_sh_prepare

Description:

Certificate CA:
1) letsencrypt
2) letsencrypt_test
3) buypass
4) buypass_test
5) zerossl
6) sslcom
7) google
8) googletest
9) Manual
Choice: 2

Description:

Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
2) Manual
Choice: 1
Email account:
michimussato@gmail.com
ClouDNS Auth ID: 44124
ClouDNS Auth Password: helloworld
root > Contents Pi-hole docker-compose.yml: 
services:                                                                                                                                                                                                          
  acme-sh-openstudiolandscapes-cloud-ip-cc:                                                                                                                                                                        
    command:                                                                                                                                                                                                       
    - daemon                                                                                                                                                                                                       
    container_name: acme-sh-openstudiolandscapes-cloud-ip-cc                                                                                                                                                       
    domainname: openstudiolandscapes.lan                                                                                                                                                                           
    environment:                                                                                                                                                                                                   
      ACME_SH_CA: letsencrypt_test                                                                                                                                                                                 
      ACME_SH_CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                             
      ACME_SH_CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                    
      ACME_SH_EMAIL: michimussato@gmail.com                                                                                                                                                                        
      ACME_SH_TLD: openstudiolandscapes.cloud-ip.cc                                                                                                                                                                
      CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                                     
      CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                            
    hostname: acme-sh-openstudiolandscapes-cloud-ip-cc.farm.evil                                                                                                                                                   
    image: docker.io/neilpang/acme.sh                                                                                                                                                                              
    network_mode: host                                                                                                                                                                                             
    restart: always                                                                                                                                                                                                
    stdin_open: true                                                                                                                                                                                               
    tty: true                                                                                                                                                                                                      
    volumes:                                                                                                                                                                                                       
    - /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs:/acme.sh:rw                                                                                         
                                                                                                                                                                                                                   
root > docker-compose.yml created: 
/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml                                                                                              
nox > Session acme_sh_prepare was successful in 20 seconds.
nox > Running session acme_sh_up_detach
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpsoi1npqk/acme_sh_up_detach

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'up', '--remove-orphans', '--detach']                                                                                                 
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc up --remove-orphans --detach                                                                                                                                          
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Creating
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Created
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Starting
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Started
nox > Session acme_sh_up_detach was successful in 2 seconds.
nox > Running session acme_sh_register_account
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpsoi1npqk/acme_sh_register_account

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
nox > container_env = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'acme-sh-openstudiolandscapes-cloud-ip-cc.farm.evil', 'ACME_SH_CA': 'letsencrypt_test', 'ACME_SH_CLOUDNS_AUTH_ID': '44124', 'ACME_SH_CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_EMAIL': 'michimussato@gmail.com', 'ACME_SH_TLD': 'openstudiolandscapes.cloud-ip.cc', 'CLOUDNS_AUTH_ID': '44124', 'CLOUDNS_AUTH_PASSWORD': 'helloworld', 'LE_CONFIG_HOME': '/acme.sh', 'AUTO_UPGRADE': '1', 'HOME': '/root'}                                                                                                                               
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --register-account --server $ACME_SH_CA --email $ACME_SH_EMAIL'
[Mon Nov  3 11:30:33 UTC 2025] Account key creation OK.
[Mon Nov  3 11:30:33 UTC 2025] Registering account: https://acme-staging-v02.api.letsencrypt.org/directory
[Mon Nov  3 11:30:35 UTC 2025] Registered
[Mon Nov  3 11:30:35 UTC 2025] ACCOUNT_THUMBPRINT='Zoufwyr_e-5KqwV8O6OA42PVXOwydB6r0YzgneCppDU'
nox > Session acme_sh_register_account was successful in 3 seconds.
nox > Running session acme_sh_create_certificate
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpsoi1npqk/acme_sh_create_certificate

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
nox > container_env = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'acme-sh-openstudiolandscapes-cloud-ip-cc.farm.evil', 'ACME_SH_CA': 'letsencrypt_test', 'ACME_SH_CLOUDNS_AUTH_ID': '44124', 'ACME_SH_CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_EMAIL': 'michimussato@gmail.com', 'ACME_SH_TLD': 'openstudiolandscapes.cloud-ip.cc', 'CLOUDNS_AUTH_ID': '44124', 'CLOUDNS_AUTH_PASSWORD': 'helloworld', 'LE_CONFIG_HOME': '/acme.sh', 'AUTO_UPGRADE': '1', 'HOME': '/root'}                                                                                                                               
Sub-Domains (comma-separated):
Top Level Domain: openstudiolandscapes.cloud-ip.cc
Sub-Domains: teleport.,*.teleport.
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --issue --server $ACME_SH_CA --force --dns dns_cloudns --domain openstudiolandscapes.cloud-ip.cc --domain teleport.openstudiolandscapes.cloud-ip.cc --domain *.teleport.openstudiolandscapes.cloud-ip.cc'                                                                                                                                          
[Mon Nov  3 11:30:47 UTC 2025] Using CA: https://acme-staging-v02.api.letsencrypt.org/directory
[Mon Nov  3 11:30:47 UTC 2025] Creating domain key
[Mon Nov  3 11:30:47 UTC 2025] The domain key is here: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.key
[Mon Nov  3 11:30:47 UTC 2025] Multi domain='DNS:openstudiolandscapes.cloud-ip.cc,DNS:teleport.openstudiolandscapes.cloud-ip.cc,DNS:*.teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:30:50 UTC 2025] Getting webroot for domain='openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:30:50 UTC 2025] Getting webroot for domain='teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:30:50 UTC 2025] Getting webroot for domain='*.teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:30:50 UTC 2025] Adding TXT value: nMxmWdS-dZvSue84lQi_guNUQmVfmubKhKutEwci8ZY for domain: _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:30:50 UTC 2025] Using cloudns
[Mon Nov  3 11:30:50 UTC 2025] Adding the TXT record for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:30:50 UTC 2025] Added.
[Mon Nov  3 11:30:50 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 11:30:50 UTC 2025] Adding TXT value: yg2yIdFZOLD3-QHl8uXbqmS8QA7c7PE8n5b43I5ElhA for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:30:50 UTC 2025] Using cloudns
[Mon Nov  3 11:30:50 UTC 2025] Adding the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:30:50 UTC 2025] Added.
[Mon Nov  3 11:30:50 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 11:30:50 UTC 2025] Adding TXT value: YMvIfTfhuRHTNPWyw2laNO13mUPm8Way1r24uhcKlho for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:30:50 UTC 2025] Using cloudns
[Mon Nov  3 11:30:51 UTC 2025] Adding the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:30:51 UTC 2025] Added.
[Mon Nov  3 11:30:51 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 11:30:51 UTC 2025] Let's check each DNS record now. Sleeping for 20 seconds first.
[Mon Nov  3 11:31:11 UTC 2025] You can use '--dnssleep' to disable public dns checks.
[Mon Nov  3 11:31:11 UTC 2025] See: https://github.com/acmesh-official/acme.sh/wiki/dnscheck
[Mon Nov  3 11:31:11 UTC 2025] Checking openstudiolandscapes.cloud-ip.cc for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:11 UTC 2025] Success for domain openstudiolandscapes.cloud-ip.cc '_acme-challenge.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 11:31:11 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:11 UTC 2025] Success for domain teleport.openstudiolandscapes.cloud-ip.cc '_acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 11:31:11 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:11 UTC 2025] Success for domain teleport.openstudiolandscapes.cloud-ip.cc '_acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 11:31:11 UTC 2025] All checks succeeded
[Mon Nov  3 11:31:11 UTC 2025] Verifying: openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:12 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 11:31:14 UTC 2025] Success
[Mon Nov  3 11:31:14 UTC 2025] Verifying: teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:15 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 11:31:18 UTC 2025] Success
[Mon Nov  3 11:31:18 UTC 2025] Verifying: *.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:18 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 11:31:21 UTC 2025] Success
[Mon Nov  3 11:31:21 UTC 2025] Removing DNS records.
[Mon Nov  3 11:31:21 UTC 2025] Removing txt: nMxmWdS-dZvSue84lQi_guNUQmVfmubKhKutEwci8ZY for domain: _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:21 UTC 2025] Using cloudns
[Mon Nov  3 11:31:21 UTC 2025] Deleting the TXT record for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:21 UTC 2025] Deleted.
[Mon Nov  3 11:31:21 UTC 2025] Successfully removed
[Mon Nov  3 11:31:21 UTC 2025] Removing txt: yg2yIdFZOLD3-QHl8uXbqmS8QA7c7PE8n5b43I5ElhA for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:21 UTC 2025] Using cloudns
[Mon Nov  3 11:31:22 UTC 2025] Deleting the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:22 UTC 2025] Deleted.
[Mon Nov  3 11:31:22 UTC 2025] Successfully removed
[Mon Nov  3 11:31:22 UTC 2025] Removing txt: YMvIfTfhuRHTNPWyw2laNO13mUPm8Way1r24uhcKlho for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:22 UTC 2025] Using cloudns
[Mon Nov  3 11:31:22 UTC 2025] Deleting the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:31:22 UTC 2025] Deleted.
[Mon Nov  3 11:31:22 UTC 2025] Successfully removed
[Mon Nov  3 11:31:22 UTC 2025] Verification finished, beginning signing.
[Mon Nov  3 11:31:22 UTC 2025] Let's finalize the order.
[Mon Nov  3 11:31:22 UTC 2025] Le_OrderFinalize='https://acme-staging-v02.api.letsencrypt.org/acme/finalize/239955653/28469426063'
[Mon Nov  3 11:31:23 UTC 2025] Order status is 'processing', let's sleep and retry.
[Mon Nov  3 11:31:23 UTC 2025] Sleeping for 3 seconds then retrying
[Mon Nov  3 11:31:26 UTC 2025] Polling order status: https://acme-staging-v02.api.letsencrypt.org/acme/order/239955653/28469426063
[Mon Nov  3 11:31:27 UTC 2025] Downloading cert.
[Mon Nov  3 11:31:27 UTC 2025] Le_LinkCert='https://acme-staging-v02.api.letsencrypt.org/acme/cert/2c0039e47e64cab7ac5bb95bde0834dea0c5'
[Mon Nov  3 11:31:27 UTC 2025] Cert success.
-----BEGIN CERTIFICATE-----
MIIEPDCCA8OgAwIBAgISLAA55H5kyresW7lb3gg03qDFMAoGCCqGSM49BAMDMFox
CzAJBgNVBAYTAlVTMSAwHgYDVQQKExcoU1RBR0lORykgTGV0J3MgRW5jcnlwdDEp
MCcGA1UEAxMgKFNUQUdJTkcpIE15c3RlcmlvdXMgTXVsYmVycnkgRTgwHhcNMjUx
MTAzMTAzMjUzWhcNMjYwMjAxMTAzMjUyWjArMSkwJwYDVQQDEyBvcGVuc3R1ZGlv
bGFuZHNjYXBlcy5jbG91ZC1pcC5jYzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IA
BNCavzUS61flp9wdhNUZCUZwqy7D2hLwDBQfYjLRdymcz4FT29CfSe2BD1r+TUbu
FSjhvTaq6d+2bAeDlEfglaSjggKWMIICkjAOBgNVHQ8BAf8EBAMCB4AwHQYDVR0l
BBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMAwGA1UdEwEB/wQCMAAwHQYDVR0OBBYE
FLrlvlf+hHVReR++r1KxfVRCpg/cMB8GA1UdIwQYMBaAFMlBk0JI0YwXBpHy8jnS
oB+nu9s5MDYGCCsGAQUFBwEBBCowKDAmBggrBgEFBQcwAoYaaHR0cDovL3N0Zy1l
OC5pLmxlbmNyLm9yZy8wgYMGA1UdEQR8MHqCKyoudGVsZXBvcnQub3BlbnN0dWRp
b2xhbmRzY2FwZXMuY2xvdWQtaXAuY2OCIG9wZW5zdHVkaW9sYW5kc2NhcGVzLmNs
b3VkLWlwLmNjgil0ZWxlcG9ydC5vcGVuc3R1ZGlvbGFuZHNjYXBlcy5jbG91ZC1p
cC5jYzATBgNVHSAEDDAKMAgGBmeBDAECATAxBgNVHR8EKjAoMCagJKAihiBodHRw
Oi8vc3RnLWU4LmMubGVuY3Iub3JnLzcwLmNybDCCAQsGCisGAQQB1nkCBAIEgfwE
gfkA9wB2AN2ZNPyl5ySAyVZofYE0mQhJskn3tWnYx7yrP1zB825kAAABmkl8cK8A
AAQDAEcwRQIgCmCPhHUxy9TttaS6j1YnwWB7BEFNmGRl8dfAz/rAqxsCIQD3uQNN
AzxYMQHurgqz+KTEi7uLDcmkM1QNNi6zhtK+JgB9AILNzUeed+RdFK1pA4gsQRP8
gcISE77Cs9lOncfNgM3+AAABmkl8cWMACAAABQAD4KP7BAMARjBEAiBYp6OhaHzk
O3ry8wnBRruB02Lj5BoaHhgx9g6W8t6aAAIgERkca3ZIxX615xGycYVu5+I8hTTZ
O/yCgcfycmHPQ54wCgYIKoZIzj0EAwMDZwAwZAIwQSbO5B44grFVqrvhYbEtqIgY
J35TQu6TFRwZ76yVg+dprwvLz986jcGbpb7YxVfnAjBeAzGUqyIYbA/s5lL/epUO
Rf9ImBUNzzyBFkC0No0Fg5gJcrVhmoOOvozRiYuuCQY=
-----END CERTIFICATE-----
[Mon Nov  3 11:31:27 UTC 2025] Your cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.cer
[Mon Nov  3 11:31:27 UTC 2025] Your cert key is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.key
[Mon Nov  3 11:31:27 UTC 2025] The intermediate CA cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/ca.cer
[Mon Nov  3 11:31:27 UTC 2025] And the full-chain cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/fullchain.cer
nox > Session acme_sh_create_certificate was successful in 52 seconds.
nox > Running session acme_sh_down
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpsoi1npqk/acme_sh_down

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'down']                                                                                                                               
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc down                                                                                                                                                                  
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopping
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopped
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removing
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removed
nox > Session acme_sh_down was successful in 4 seconds.
nox > Ran 5 sessions in a minute:
nox > * acme_sh_prepare: success, took 20 seconds
nox > * acme_sh_up_detach: success, took 2 seconds
nox > * acme_sh_register_account: success, took 3 seconds
nox > * acme_sh_create_certificate: success, took 52 seconds
nox > * acme_sh_down: success, took 4 seconds
```

##### `acme-sh-openstudiolandscapes-cloud-ip-cc`

```
$ nox -s acme_sh_prepare acme_sh_up_detach acme_sh_register_account acme_sh_create_certificate acme_sh_down
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
git.cmd > Popen(['git', 'version'], cwd=/home/michael/git/repos/OpenStudioLandscapes, stdin=None, shell=False, universal_newlines=False)
Using temporary directory: /tmp/tmpi2vvpl_m
nox > Running session acme_sh_prepare
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpi2vvpl_m/acme_sh_prepare

Description:

Certificate CA:
1) letsencrypt
2) letsencrypt_test
3) buypass
4) buypass_test
5) zerossl
6) sslcom
7) google
8) googletest
9) Manual
Choice: 2

Description:

Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
2) Manual
Choice: 1
Email account:
michimussato@gmail.com
ClouDNS Auth ID: 44124
ClouDNS Auth Password: helloworld
root > Contents Pi-hole docker-compose.yml: 
services:                                                                                                                                                                                                          
  acme-sh-openstudiolandscapes-cloud-ip-cc:                                                                                                                                                                        
    command:                                                                                                                                                                                                       
    - daemon                                                                                                                                                                                                       
    container_name: acme-sh-openstudiolandscapes-cloud-ip-cc                                                                                                                                                       
    domainname: openstudiolandscapes.lan                                                                                                                                                                           
    environment:                                                                                                                                                                                                   
      ACME_SH_CA: letsencrypt_test                                                                                                                                                                                 
      ACME_SH_CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                             
      ACME_SH_CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                    
      ACME_SH_EMAIL: michimussato@gmail.com                                                                                                                                                                        
      ACME_SH_TLD: openstudiolandscapes.cloud-ip.cc                                                                                                                                                                
      CLOUDNS_AUTH_ID: '44124'                                                                                                                                                                                     
      CLOUDNS_AUTH_PASSWORD: helloworld                                                                                                                                                                            
    hostname: acme-sh-openstudiolandscapes-cloud-ip-cc                                                                                                                                                             
    image: docker.io/neilpang/acme.sh                                                                                                                                                                              
    network_mode: host                                                                                                                                                                                             
    restart: always                                                                                                                                                                                                
    stdin_open: true                                                                                                                                                                                               
    tty: true                                                                                                                                                                                                      
    volumes:                                                                                                                                                                                                       
    - /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs:/acme.sh:rw                                                                                         
                                                                                                                                                                                                                   
root > docker-compose.yml created: 
/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml                                                                                              
nox > Session acme_sh_prepare was successful in 16 seconds.
nox > Running session acme_sh_up_detach
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpi2vvpl_m/acme_sh_up_detach

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'up', '--remove-orphans', '--detach']                                                                                                 
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc up --remove-orphans --detach                                                                                                                                          
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Creating
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Created
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Starting
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Started
nox > Session acme_sh_up_detach was successful in 2 seconds.
nox > Running session acme_sh_register_account
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpi2vvpl_m/acme_sh_register_account

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
nox > container_env = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'acme-sh-openstudiolandscapes-cloud-ip-cc', 'CLOUDNS_AUTH_ID': '44124', 'CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_CA': 'letsencrypt_test', 'ACME_SH_CLOUDNS_AUTH_ID': '44124', 'ACME_SH_CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_EMAIL': 'michimussato@gmail.com', 'ACME_SH_TLD': 'openstudiolandscapes.cloud-ip.cc', 'LE_CONFIG_HOME': '/acme.sh', 'AUTO_UPGRADE': '1', 'HOME': '/root'}                                                                                                                                         
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --register-account --server $ACME_SH_CA --email $ACME_SH_EMAIL'
[Mon Nov  3 11:24:45 UTC 2025] Account key creation OK.
[Mon Nov  3 11:24:45 UTC 2025] Registering account: https://acme-staging-v02.api.letsencrypt.org/directory
[Mon Nov  3 11:24:46 UTC 2025] Registered
[Mon Nov  3 11:24:46 UTC 2025] ACCOUNT_THUMBPRINT='m0xTeXAMCmy4S2AZYzW9p9xUCtMPND1XENYjbZ8AnLA'
nox > Session acme_sh_register_account was successful in 3 seconds.
nox > Running session acme_sh_create_certificate
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpi2vvpl_m/acme_sh_create_certificate

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
nox > container_env = {'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin', 'HOSTNAME': 'acme-sh-openstudiolandscapes-cloud-ip-cc', 'CLOUDNS_AUTH_ID': '44124', 'CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_CA': 'letsencrypt_test', 'ACME_SH_CLOUDNS_AUTH_ID': '44124', 'ACME_SH_CLOUDNS_AUTH_PASSWORD': 'helloworld', 'ACME_SH_EMAIL': 'michimussato@gmail.com', 'ACME_SH_TLD': 'openstudiolandscapes.cloud-ip.cc', 'LE_CONFIG_HOME': '/acme.sh', 'AUTO_UPGRADE': '1', 'HOME': '/root'}                                                                                                                                         
Sub-Domains (comma-separated):
Top Level Domain: openstudiolandscapes.cloud-ip.cc
Sub-Domains: teleport.,*.teleport.
nox > bash -c '/usr/local/bin/docker exec acme-sh-openstudiolandscapes-cloud-ip-cc --issue --server $ACME_SH_CA --force --dns dns_cloudns --domain openstudiolandscapes.cloud-ip.cc --domain teleport.openstudiolandscapes.cloud-ip.cc --domain *.teleport.openstudiolandscapes.cloud-ip.cc'                                                                                                                                          
[Mon Nov  3 11:25:04 UTC 2025] Using CA: https://acme-staging-v02.api.letsencrypt.org/directory
[Mon Nov  3 11:25:04 UTC 2025] Creating domain key
[Mon Nov  3 11:25:04 UTC 2025] The domain key is here: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.key
[Mon Nov  3 11:25:04 UTC 2025] Multi domain='DNS:openstudiolandscapes.cloud-ip.cc,DNS:teleport.openstudiolandscapes.cloud-ip.cc,DNS:*.teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:25:07 UTC 2025] Getting webroot for domain='openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:25:07 UTC 2025] Getting webroot for domain='teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:25:07 UTC 2025] Getting webroot for domain='*.teleport.openstudiolandscapes.cloud-ip.cc'
[Mon Nov  3 11:25:07 UTC 2025] Adding TXT value: Q3g7OSwrgwZHMcZ1mcLTFzfwXJbzx7HUK96nn_ImEu4 for domain: _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:07 UTC 2025] Using cloudns
[Mon Nov  3 11:25:07 UTC 2025] Adding the TXT record for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:07 UTC 2025] Added.
[Mon Nov  3 11:25:07 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 11:25:07 UTC 2025] Adding TXT value: 9GfocgHUQSddW0x0C6RhOswnrKWA3VRDMld-gIzqtNs for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:07 UTC 2025] Using cloudns
[Mon Nov  3 11:25:07 UTC 2025] Adding the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:07 UTC 2025] Added.
[Mon Nov  3 11:25:07 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 11:25:07 UTC 2025] Adding TXT value: F0Y7HizjgxWD8dEVbVR1asFgIf3A9gDKt8r2RcBzYe8 for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:07 UTC 2025] Using cloudns
[Mon Nov  3 11:25:08 UTC 2025] Adding the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:08 UTC 2025] Added.
[Mon Nov  3 11:25:08 UTC 2025] The TXT record has been successfully added.
[Mon Nov  3 11:25:08 UTC 2025] Let's check each DNS record now. Sleeping for 20 seconds first.
[Mon Nov  3 11:25:28 UTC 2025] You can use '--dnssleep' to disable public dns checks.
[Mon Nov  3 11:25:28 UTC 2025] See: https://github.com/acmesh-official/acme.sh/wiki/dnscheck
[Mon Nov  3 11:25:28 UTC 2025] Checking openstudiolandscapes.cloud-ip.cc for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:28 UTC 2025] Not valid yet, let's wait for 10 seconds then check the next one.
[Mon Nov  3 11:25:38 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:38 UTC 2025] Success for domain teleport.openstudiolandscapes.cloud-ip.cc '_acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 11:25:38 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:38 UTC 2025] Success for domain teleport.openstudiolandscapes.cloud-ip.cc '_acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 11:25:38 UTC 2025] Let's wait for 10 seconds and check again.
[Mon Nov  3 11:25:48 UTC 2025] You can use '--dnssleep' to disable public dns checks.
[Mon Nov  3 11:25:48 UTC 2025] See: https://github.com/acmesh-official/acme.sh/wiki/dnscheck
[Mon Nov  3 11:25:48 UTC 2025] Checking openstudiolandscapes.cloud-ip.cc for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:48 UTC 2025] Success for domain openstudiolandscapes.cloud-ip.cc '_acme-challenge.openstudiolandscapes.cloud-ip.cc'.
[Mon Nov  3 11:25:48 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:48 UTC 2025] Already succeeded, continuing.
[Mon Nov  3 11:25:48 UTC 2025] Checking teleport.openstudiolandscapes.cloud-ip.cc for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:48 UTC 2025] Already succeeded, continuing.
[Mon Nov  3 11:25:48 UTC 2025] All checks succeeded
[Mon Nov  3 11:25:48 UTC 2025] Verifying: openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:49 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 11:25:52 UTC 2025] Success
[Mon Nov  3 11:25:52 UTC 2025] Verifying: teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:52 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 11:25:55 UTC 2025] Success
[Mon Nov  3 11:25:55 UTC 2025] Verifying: *.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:55 UTC 2025] Pending. The CA is processing your order, please wait. (1/30)
[Mon Nov  3 11:25:58 UTC 2025] Success
[Mon Nov  3 11:25:58 UTC 2025] Removing DNS records.
[Mon Nov  3 11:25:58 UTC 2025] Removing txt: Q3g7OSwrgwZHMcZ1mcLTFzfwXJbzx7HUK96nn_ImEu4 for domain: _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:58 UTC 2025] Using cloudns
[Mon Nov  3 11:25:58 UTC 2025] Deleting the TXT record for _acme-challenge.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:58 UTC 2025] Deleted.
[Mon Nov  3 11:25:58 UTC 2025] Successfully removed
[Mon Nov  3 11:25:58 UTC 2025] Removing txt: 9GfocgHUQSddW0x0C6RhOswnrKWA3VRDMld-gIzqtNs for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:58 UTC 2025] Using cloudns
[Mon Nov  3 11:25:59 UTC 2025] Deleting the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:59 UTC 2025] Deleted.
[Mon Nov  3 11:25:59 UTC 2025] Successfully removed
[Mon Nov  3 11:25:59 UTC 2025] Removing txt: F0Y7HizjgxWD8dEVbVR1asFgIf3A9gDKt8r2RcBzYe8 for domain: _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:59 UTC 2025] Using cloudns
[Mon Nov  3 11:25:59 UTC 2025] Deleting the TXT record for _acme-challenge.teleport.openstudiolandscapes.cloud-ip.cc
[Mon Nov  3 11:25:59 UTC 2025] Deleted.
[Mon Nov  3 11:25:59 UTC 2025] Successfully removed
[Mon Nov  3 11:25:59 UTC 2025] Verification finished, beginning signing.
[Mon Nov  3 11:25:59 UTC 2025] Let's finalize the order.
[Mon Nov  3 11:25:59 UTC 2025] Le_OrderFinalize='https://acme-staging-v02.api.letsencrypt.org/acme/finalize/239954723/28469305113'
[Mon Nov  3 11:26:00 UTC 2025] Order status is 'processing', let's sleep and retry.
[Mon Nov  3 11:26:00 UTC 2025] Sleeping for 3 seconds then retrying
[Mon Nov  3 11:26:03 UTC 2025] Polling order status: https://acme-staging-v02.api.letsencrypt.org/acme/order/239954723/28469305113
[Mon Nov  3 11:26:04 UTC 2025] Downloading cert.
[Mon Nov  3 11:26:04 UTC 2025] Le_LinkCert='https://acme-staging-v02.api.letsencrypt.org/acme/cert/2cd413fee9bc0ae331b010d1bf4629bf13eb'
[Mon Nov  3 11:26:04 UTC 2025] Cert success.
-----BEGIN CERTIFICATE-----
MIIEPzCCA8WgAwIBAgISLNQT/um8CuMxsBDRv0YpvxPrMAoGCCqGSM49BAMDMFox
CzAJBgNVBAYTAlVTMSAwHgYDVQQKExcoU1RBR0lORykgTGV0J3MgRW5jcnlwdDEp
MCcGA1UEAxMgKFNUQUdJTkcpIE15c3RlcmlvdXMgTXVsYmVycnkgRTgwHhcNMjUx
MTAzMTAyNzMwWhcNMjYwMjAxMTAyNzI5WjArMSkwJwYDVQQDEyBvcGVuc3R1ZGlv
bGFuZHNjYXBlcy5jbG91ZC1pcC5jYzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IA
BFR++CLC0TJ4enkZ9lubqt9yp9KvSnrEb21w5Sb+ZvfHz88ybS1S4U7uRacJo+1J
Yw4VZb3HsJgr/M0zBsPrwO2jggKYMIIClDAOBgNVHQ8BAf8EBAMCB4AwHQYDVR0l
BBYwFAYIKwYBBQUHAwEGCCsGAQUFBwMCMAwGA1UdEwEB/wQCMAAwHQYDVR0OBBYE
FHCZKi52einNdRFffMMF+tDoMQmMMB8GA1UdIwQYMBaAFMlBk0JI0YwXBpHy8jnS
oB+nu9s5MDYGCCsGAQUFBwEBBCowKDAmBggrBgEFBQcwAoYaaHR0cDovL3N0Zy1l
OC5pLmxlbmNyLm9yZy8wgYMGA1UdEQR8MHqCKyoudGVsZXBvcnQub3BlbnN0dWRp
b2xhbmRzY2FwZXMuY2xvdWQtaXAuY2OCIG9wZW5zdHVkaW9sYW5kc2NhcGVzLmNs
b3VkLWlwLmNjgil0ZWxlcG9ydC5vcGVuc3R1ZGlvbGFuZHNjYXBlcy5jbG91ZC1p
cC5jYzATBgNVHSAEDDAKMAgGBmeBDAECATAyBgNVHR8EKzApMCegJaAjhiFodHRw
Oi8vc3RnLWU4LmMubGVuY3Iub3JnLzEwOC5jcmwwggEMBgorBgEEAdZ5AgQCBIH9
BIH6APgAdwAW6GnB0ZXq18P4lxrj8HYB94zhtp0xqFIYtoN/MagVCAAAAZpJd4K1
AAAEAwBIMEYCIQDVYZNAjwS1Je+W1uYtH/a65KJQHOXTN+38Tokyekw7MgIhAMls
oK7tDawAIBa90IFa9wKCGjkGAYw/3EPVGBahHEGsAH0Ags3NR5535F0UrWkDiCxB
E/yBwhITvsKz2U6dx82Azf4AAAGaSXeKsgAIAAAFAAPgg3YEAwBGMEQCIDO10LAv
hBKXmuvG0in6dkLMG/rtgZLCN6DUTf5A0c3eAiB+4e8eRZp1DGEyFkhI/8H7/21I
cmA0HU8UdIBx8WzJJTAKBggqhkjOPQQDAwNoADBlAjA1S2NXSP+xkbBJdDEWF5PM
Fn/ibRjzmS895+8AjZG/LBmMZz2NLgi7XJZDdh6ViIwCMQCcowlkC2z9zdl/dx1M
U0X9H18b5vmL1d68w1h7ejY6iN9nQVnISxeQFHV2zukdJLM=
-----END CERTIFICATE-----
[Mon Nov  3 11:26:04 UTC 2025] Your cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.cer
[Mon Nov  3 11:26:04 UTC 2025] Your cert key is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/openstudiolandscapes.cloud-ip.cc.key
[Mon Nov  3 11:26:04 UTC 2025] The intermediate CA cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/ca.cer
[Mon Nov  3 11:26:04 UTC 2025] And the full-chain cert is in: /acme.sh/openstudiolandscapes.cloud-ip.cc_ecc/fullchain.cer
nox > Session acme_sh_create_certificate was successful in a minute.
nox > Running session acme_sh_down
nox > Creating virtual environment (virtualenv) using python in /tmp/tmpi2vvpl_m/acme_sh_down

Description:

Available Top Level Domain:
1) openstudiolandscapes.cloud-ip.cc
Choice: 1
nox > tld = 'openstudiolandscapes.cloud-ip.cc'
root > cmd = ['/usr/local/bin/docker', 'compose', '--progress', 'plain', '--file', '/home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml', '--project-name', 'openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc', 'down']                                                                                                                               
nox > /usr/local/bin/docker compose --progress plain --file /home/michael/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/docker-compose.yml --project-name openstudiolandscapes-acme-sh--openstudiolandscapes-cloud-ip-cc down                                                                                                                                                                  
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopping
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Stopped
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removing
 Container acme-sh-openstudiolandscapes-cloud-ip-cc  Removed
nox > Session acme_sh_down was successful in 6 seconds.
nox > Ran 5 sessions in a minute:
nox > * acme_sh_prepare: success, took 16 seconds
nox > * acme_sh_up_detach: success, took 2 seconds
nox > * acme_sh_register_account: success, took 3 seconds
nox > * acme_sh_create_certificate: success, took a minute
nox > * acme_sh_down: success, took 6 second
```

## File Structure

### Certificate CA

#### `letsencrypt`

##### acme.sh

```
$ tree ~/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs
~/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs
├── account.conf
├── ca
│    └── acme-v02.api.letsencrypt.org
│        └── directory
│            ├── account.json
│            ├── account.key
│            └── ca.conf
├── http.header
└── openstudiolandscapes.cloud-ip.cc_ecc
    ├── ca.cer
    ├── fullchain.cer
    ├── openstudiolandscapes.cloud-ip.cc.cer
    ├── openstudiolandscapes.cloud-ip.cc.conf
    ├── openstudiolandscapes.cloud-ip.cc.csr
    ├── openstudiolandscapes.cloud-ip.cc.csr.conf
    └── openstudiolandscapes.cloud-ip.cc.key

5 directories, 12 files
```

#### `letsencrypt_test`

##### acme.sh

```
$ tree ~/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs
~/git/repos/OpenStudioLandscapes/.landscapes/.acme.sh/openstudiolandscapes.cloud-ip.cc/certs
├── account.conf
├── ca
│   └── acme-staging-v02.api.letsencrypt.org
│       └── directory
│           ├── account.json
│           ├── account.key
│           └── ca.conf
├── http.header
└── openstudiolandscapes.cloud-ip.cc_ecc
    ├── ca.cer
    ├── fullchain.cer
    ├── openstudiolandscapes.cloud-ip.cc.cer
    ├── openstudiolandscapes.cloud-ip.cc.conf
    ├── openstudiolandscapes.cloud-ip.cc.csr
    ├── openstudiolandscapes.cloud-ip.cc.csr.conf
    └── openstudiolandscapes.cloud-ip.cc.key

5 directories, 12 files
```

##### Caddy

```
tree ~/git/repos/OpenStudioLandscapes-Infra/caddy/ClouDNS/volumes/data/caddy
~/git/repos/OpenStudioLandscapes-Infra/caddy/ClouDNS/volumes/data/caddy
├── acme
│   └── acme-staging-v02.api.letsencrypt.org-directory
│       └── users
│           └── michimussato@gmail.com
│               ├── michimussato.json
│               └── michimussato.key
├── certificates
│   └── acme-staging-v02.api.letsencrypt.org-directory
│       ├── teleport.openstudiolandscapes.cloud-ip.cc
│       │   ├── teleport.openstudiolandscapes.cloud-ip.cc.crt
│       │   ├── teleport.openstudiolandscapes.cloud-ip.cc.json
│       │   └── teleport.openstudiolandscapes.cloud-ip.cc.key
│       └── wildcard_.teleport.openstudiolandscapes.cloud-ip.cc
│           ├── wildcard_.teleport.openstudiolandscapes.cloud-ip.cc.crt
│           ├── wildcard_.teleport.openstudiolandscapes.cloud-ip.cc.json
│           └── wildcard_.teleport.openstudiolandscapes.cloud-ip.cc.key
├── instance.uuid
├── last_clean.json
└── locks

10 directories, 10 files
```