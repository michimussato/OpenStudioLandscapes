<!-- TOC -->
* [Dependency Overview (schematic)](#dependency-overview-schematic)
<!-- TOC -->

---

# Dependency Overview (schematic)

```mermaid
%% https://mermaid-js.github.io/mermaid-live-editor
flowchart TB
%%    OpenStudioLandscapes((OpenStudioLandscapes))
    ubuntu((Ubuntu))
%%    linux((Linux))
    
    subgraph osl[OpenStudioLandscapes]
        direction TB
        
        subgraph Core 
            direction TB
    
            subgraph dagstersubgraph[Dagster]
                direction TB
                dagster((Dagster))
                dagster-postgres((Postgres))
            end
            
        end
        
        subgraph Sub Systems 
            direction TB
        
            subgraph zerotrustmfa[Zero Trust MFA]
                direction TB
                    teleport((Teleport))
            end
        
            subgraph local-registry[Container Registry]
                direction TB
                    harbor((Harbor))
            end
            
%%            subgraph Docker Registry
%%                direction TB
%%                dockerio((Docker.io))
%%                
%%            end
            
%%            subgraph DNS Server
%%                direction TB
%%                pihole((Pi-hole))
%%            end
            
        end
        
    end
    
    dagster -- requires --> dagster-postgres
    
    subgraph linux[Linux]
        direction TB
    
        subgraph linuxpkgs[Linux Packages]
            direction LR
            systemd(systemd)
            make(make)
            git(git)
            graphviz(GraphViz)
            sudo(sudo)
            docker(Docker)
            python(python3.11)
        end
%%        systemd(systemd)
%%        make(make)
%%        git(git)
%%        graphviz(GraphViz)
%%        sudo(sudo)
%%        docker(Docker)
%%        python(python3.11)
    end
    
    subgraph external-registry[External Registries]
        direction LR
        alibaba(Alibaba Cloud ACR)
        aws(Aws ECR)
        azure(ACR)
        dockerhub(Docker Hub)
        dockerregistry(Docker Registry)
        dtr(DTR)
        github(Github GHCR)
        gitlab(Gitlab)
        google(Google GCR)
        harbor_(Harbor)
        huawei(Huawei SWR)
        jfrog(JFrog Artifactory)
        quay(Quay)
        tencent(Tencent TCR)
        volcengine(VolcEngine CR)
    end
    
    subgraph dns[DNS Server]
        direction TB
        pihole((Pi-hole))
    end
        
    subgraph features[OpenStudioLandscapes Features]
        direction TB
    
        subgraph public[Released]
            direction LR
            osl-ayon(OpenStudioLandscapes-Ayon)
            osl-dagster(OpenStudioLandscapes-Dagster)
            osl-kitsu(OpenStudioLandscapes-Kitsu)
            osl-rustdeskserver(OpenStudioLandscapes-RustDeskServer)
        end
    
        subgraph private[Not Released]
            direction LR
    
            subgraph template[Template]
                direction LR
                osl-template(OpenStudioLandscapes-Template)
            end
            osl-deadline-10-2(OpenStudioLandscapes-Deadline-10-2)
            osl-deadline-10-2-worker(OpenStudioLandscapes-Deadline-10-2-Worker)
%%            osl-deadline-10-2-worker -- requires --> osl-deadline-10-2
            osl-filebrowser(OpenStudioLandscapes-filebrowser)
            osl-grafana(OpenStudioLandscapes-Grafana)
            osl-likec4(OpenStudioLandscapes-LikeC4)
            osl-nukerlm-8(OpenStudioLandscapes-NukeRLM-8)
            osl-opencue(OpenStudioLandscapes-OpenCue)
            osl-sesi-gcc-9-3-houdini-20(OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20)
            osl-syncthing(OpenStudioLandscapes-Syncthing)
            osl-teleport(OpenStudioLandscapes-Teleport)
            osl-twingate(OpenStudioLandscapes-Twingate)
            osl-watchtower(OpenStudioLandscapes-Watchtower)
%%            osl-watchtower -- requires --> osl-kitsu
        end
    end
        
    
    harbor -. can replicate to .-> external-registry
%%    OpenStudioLandscapes -. recommends .-> teleport
%%    root -- requires --> docker
%%    root -- requires --> python
%%    root -- requires --> systemd
%%    root -- requires --> make
%%    root -- requires --> git
%%    root -- requires --> sudo
    osl -- requires --> linux
    osl -. recommends .-> dns
    osl -. provides .-> features
%%    git -- requires --> linux
%%    sudo -- requires --> linux
%%    make -- requires --> linux
    
%%    ubuntu -- provides --> git
%%    ubuntu -- provides --> systemd
%%    ubuntu -- provides --> make
%%    ubuntu -- provides --> graphviz
%%    ubuntu -- provides --> sudo
%%    ubuntu -- provides --> python
%%    ubuntu -- provides --> docker
    linux -. recommends .-> ubuntu
    
    
    
%%    root -. recommends .-> utuntu
%%    root -. recommends .-> pihole
```