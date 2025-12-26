# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Reference System](#reference-system)
  * [Unattended Upgrades](#unattended-upgrades)
  * [Requirements](#requirements)
    * [Ubuntu](#ubuntu)
      * [22.04](#2204)
<!-- TOC -->

---

# Reference System

- Ubuntu
  - [22.04 LTS (Jammy Jellyfish)](https://www.releases.ubuntu.com/22.04/)
    - ✅ Server
    - ✅ Desktop

> [!TIP]
> 
> Install Ubuntu as a VM to play around with OpenStudioLandscapes.
> Personally, I've been working with [VirtualBox](https://www.virtualbox.org/)
> but any compatible hypervisor should do.
> Here's a good [overview](https://en.wikipedia.org/wiki/Comparison_of_platform_virtualization_software).

## Unattended Upgrades

If you see errors like

```
[...]
E: Could not get lock /var/lib/dpkg/lock-frontend. It is held by process 5198 (unattended-upgr)
N: Be aware that removing the lock file is not a solution and may break your system.
E: Unable to acquire the dpkg frontend lock (/var/lib/dpkg/lock-frontend), is another process using it?
[...]
```

or

```
[...]
Waiting for cache lock: Could not get lock /var/lib/dpkg/lock-frontend. It is held by process 3450 (unattended-upgr)
[...]
```

during the setup processes, this indicates that Ubuntu is running unattended
upgrades in the background. This can be annoying at times. 

> [!TIP]
> 
> A way to disable this behaviour is described 
> [here](https://linuxconfig.org/disable-automatic-updates-on-ubuntu-22-04-jammy-jellyfish-linux)

## Requirements

See [Dependencies](../dependencies.md)

> [!IMPORTANT]
> 
> Installation and running commands as `root` is not allowed!
> Reference: https://github.com/michimussato/OpenStudioLandscapes/issues/2

### Ubuntu

#### 22.04

| Image   | Installer Options                                                                  |
|---------|------------------------------------------------------------------------------------|
| Desktop | ![Install_UbuntuDesktop2204.png](../../media/images/Install_UbuntuDesktop2204.png) |
| Server  | ![Install_UbuntuServer2204.png](../../media/images/Install_UbuntuServer2204.png)   |
