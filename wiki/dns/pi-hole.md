<!-- TOC -->
* [Pi-hole](#pi-hole)
  * [DNS Records](#dns-records)
    * [A-Records](#a-records)
    * [CNAME-Records](#cname-records)
<!-- TOC -->

---

# Pi-hole

## DNS Records

### A-Records

```
192.168.178.195 openstudiolandscapes.lan
```

### CNAME-Records

For some reason, wildcards don't seem to work

```
*.openstudiolandscapes.lan,openstudiolandscapes.lan
```

Therefore, all records are manual for now.

To batch add records, switch to `Expert` and add
needed records to `dns.cnameRecords` (see `All Settings`).

Core records:

```
openstudiolandscapes-dagster.openstudiolandscapes.lan,openstudiolandscapes.lan
openstudiolandscapes-dagster-postgres.openstudiolandscapes.lan,openstudiolandscapes.lan
openstudiolandscapes-harbor.openstudiolandscapes.lan,openstudiolandscapes.lan
openstudiolandscapes-teleport.openstudiolandscapes.lan,openstudiolandscapes.lan
```

Feature records:

```
ayon.openstudiolandscapes.lan,openstudiolandscapes.lan
dagster.openstudiolandscapes.lan,openstudiolandscapes.lan
deadline-10-2.openstudiolandscapes.lan,openstudiolandscapes.lan
deadline-10-2-worker.openstudiolandscapes.lan,openstudiolandscapes.lan
filebrowser.openstudiolandscapes.lan,openstudiolandscapes.lan
grafana.openstudiolandscapes.lan,openstudiolandscapes.lan
kitsu.openstudiolandscapes.lan,openstudiolandscapes.lan
nuke-rlm-8.openstudiolandscapes.lan,openstudiolandscapes.lan
sesi-gcc-9-3-houdini-20.openstudiolandscapes.lan,openstudiolandscapes.lan
syncthing.openstudiolandscapes.lan,openstudiolandscapes.lan
watchtower.openstudiolandscapes.lan,openstudiolandscapes.lan
```

Inactive records:

```
likec4.openstudiolandscapes.lan,openstudiolandscapes.lan
opencue-web.openstudiolandscapes.lan,openstudiolandscapes.lan
twingate.openstudiolandscapes.lan,openstudiolandscapes.lan
template.openstudiolandscapes.lan,openstudiolandscapes.lan
```

To check:
- [ ] OpenStudioLandscapes-RustDeskServer
