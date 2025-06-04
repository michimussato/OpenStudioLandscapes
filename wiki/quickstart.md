> [!WARNING]
> The setup script **WILL** change your system.   
> It is recommended you start with a vanilla OS.  

For now, the `OpenStudioLandscapes` installer _officially_ only supports  
Ubuntu Desktop 22.04. More Linux distros will come based on requests.  

| Distro  | Base   | Version | Tested | Supported |
|---------|--------|---------|--------|-----------|
| Ubuntu  | Debian | 22.04   | ☑      | ☑         |
| Manjaro | Arch   |         | ☒      | ☐         |
|         |        |         |        |           |

### Ubuntu Desktop
  
> [!NOTE]
> The installation process can be time-consuming. Tests show that
> the setup routine will download between 2-3 GB of data.
> And this applies only to the basic installation. Using
> OpenStudioLandscapes implies even more data transfers.
  
#### 22.04  
  
##### Desktop  
  
![Install_UbuntuDesktop2204.png](../media/images/Install_UbuntuDesktop2204.png)  
  
If you see the following, select all except `none of the above`:  
  
```  
Restarting services...  
Daemons using outdated libraries  
--------------------------------  
  
  1. dbus.service                 5. ssh.service  2. multipathd.service           6. systemd-logind.service  3. networkd-dispatcher.service  7. user@1000.service  4. polkit.service               8. none of the above  
(Enter the items or ranges you want to select, separated by spaces.)  
  
Which services should be restarted? 1-7  
```  
  
##### Server  
  
![Install_UbuntuServer2204.png](../media/images/Install_UbuntuServer2204.png)  
  
##### Requirements

- `python3`
- `curl`
- `sudo`
  
```bash  
sudo apt-get install -y curl python3 sudo
```  
  
##### Installation  
  
```bash  
python3 <(curl --header 'Cache-Control: no-cache, no-store' --silent https://raw.githubusercontent.com/michimussato/OpenStudioLandscapes-Temp/refs/heads/main/ubuntu/22.04/install_ubuntu_2204.py)
# Todo:  
#  - [ ] python3 <(curl --header 'Cache-Control: no-cache, no-store' --silent https://raw.githubusercontent.com/michimussato/OpenStudioLandscapes/refs/heads/main/ubuntu/22.04/install_ubuntu_2204.py)  
```  
  
> [!IMPORTANT]  
> The first thing the installer checks is whether `$USER` is a member of the group `docker`.  
> If the user isn't, the installer makes sure the user is. It is **mandatory** to perform  
> a reboot after that. Otherwise, the installer will produce errors when installing   
> the latest Docker binaries. Just reboot here if you are being asked to and   
> then re-run above command.  
  
Go through the setup process all the way to the end and reboot your machine.  
Log in with the user who performed the installation.  
  
##### Configure Features  
  
By default, only
- `OpenStudioLandscapes-Dagster`
- `OpenStudioLandscapes-Ayon`
- `OpenStudioLandscapes-Kitsu`
are enabled. Others might need individual configuration  
and do not work out of the box. More info in the  
`README.md` files of the Feature.  
  
Nevertheless, whether a Feature is enabled or not can be   
specified in: `OpenStudioLandscapes.engine.constants.FEATURES`  
  
##### Run OpenStudioLandscapes  
  
```bash  
openstudiolandscapes  
```  
  
Open the Dagster UI: [http://<ip_openstudiolandscapes_host>:3000/asset-groups]()  
  
Next steps:  
- [Understanding the Daster Linage](overview.md#dagster-lineage)  
- [Landscape Map: `docker-compose-graph`](overview.md#docker-compose-graph)  
- [Create Landscape](overview.md#create-landscape)