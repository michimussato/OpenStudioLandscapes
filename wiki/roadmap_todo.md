- [ ] Landscape generation based on [VFX Reference Platform](https://vfxplatform.com/) spec?
- [ ] Integrating [Rez](https://github.com/AcademySoftwareFoundation/rez)?
- Integrating Render Managers
  - Deadline
    - [x] 10.2
    - [ ] 10.3
    - [ ] 10.4
  - [x] [OpenCue](https://github.com/AcademySoftwareFoundation/OpenCue)
  - [ ] [Tractor](https://rmanwiki-26.pixar.com/space/TRA)
  - [ ] [Flamenco](https://flamenco.blender.org/)
- Dynamic Documentation
  - [ ] [LikeC4-Map](https://likec4.dev/)
- Third Party Container Integration
  - [x] [Watchtower](https://watchtower.blender.org/)
- [ ] Implement Caddy for HTTPS
  - https://caddyserver.com/
  - https://github.com/caddyserver/caddy
  - https://hub.docker.com/_/caddy
- [x] Create a `.blend` video template file
      for screen recordings.
- [ ] A weekly video with instructions
- [x] Integrate Harbor
- [ ] Clean up this `README.md`
  - [ ] Separate Readme from Documentation (Sphinx)
- [ ] Implement tests (`noxfile.py`)
- [x] Improve Feature discovery
- [ ] Implement framework-wide terminology and glossary:
  - [x] "Feature"
  - [x] "Landscape"
  - [ ] "Engine"
- [x] Jump-Start / Quick-Start
- [x] Separate README.md content
  - [x] Batch stuff to OpenStudioLandscapes README.md
  - [x] Non batch stuff (single lines) to Feature README.md
- [ ] Migrate to `pyproject.toml` exclusively?
- [x] Quote `pip install`s (`zsh: no matches found: .[dev]`)
  - `pip install ".[dev]"` works in `zsh`
- [ ] Make procedural `/home/michael/git/repos/OpenStudioLandscapes/.features` -> `{DOT_FEATURES}`:
  - From Kitsu README:
    ```
    KITSU_POSTGRES_CONF	str	/home/michael/git/repos/OpenStudioLandscapes/.features/OpenStudioLandscapes-Kitsu/.payload/config/etc/postgresql/14/main/postgresql.conf
    ```
- [x] Replace `python-on-whales` with something more lightweight/reliable
- [ ] Restrict Ubuntu 20.04 dependency to Deadline (the reason for this restriction
- [ ] Strategy to version control dynamically created files like
  - `.landscapes/.pi-hole/etc-pihole/pihole.toml`
  - `.dagster-postgres/dagster.yaml`
  - `.dagster-postgres/docker-compose.yml`
  - etc.
- Secrets
  - [x] Remove `SECRETS` 
  - [ ] Implement `.env` or something similar
- [x] Remove `michimussato@gmail.com` as default Kitsu account
- [ ] Add VPN Server?
- Harbor
  - [x] Use Harbor API to create Project `openstudiolandscapes` by default
  - [HTTPS for Harbor](https://goharbor.io/docs/2.0.0/install-config/configure-https/)
- [ ] Investigate OpenStudioLandscapes Docker image
- Linux Distro Installer
  - [x] Ubuntu Desktop 22.04
  - [ ] Ubuntu Server 22.04
- Sphinx/ReadTheDocs
  - [x] abandoned (for now)
  - [ ] Contributing
  - [ ] Changelog
- OpenStudioLandscapes-Grafana
  - [ ] clean/move/delete `./configs`
- Changelog
  - [ ] https://www.freecodecamp.org/news/a-beginners-guide-to-git-what-is-a-changelog-and-how-to-generate-it/
- Fix:
  - [ ] ```shell
       #44 5.284 
       #44 5.284           ********************************************************************************
       #44 5.284           Pattern 'LICENSE.txt' did not match any files.
       #44 5.284 
       #44 5.284           By 2026-Mar-20, you need to update your project and remove deprecated calls
       #44 5.284           or your builds will no longer be supported.
       #44 5.284           ********************************************************************************
       #44 5.285 
       #44 5.285   !!
       ```
