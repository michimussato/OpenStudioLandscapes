
---

# Installation Overview

```mermaid
graph TB
    installation_paths((Installation Paths))
    manual[Manual]
    click manual href "/basic_installation.md"
    docker[Docker]
    installer_script[Installer Script]
    installation_paths --> manual
    installation_paths --> docker
    installation_paths --> installer_script
```