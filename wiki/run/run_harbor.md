# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Launch Harbor](#launch-harbor)
  * [nox](#nox)
    * [up](#up)
      * [detached](#detached)
    * [down](#down)
  * [Web Interface](#web-interface)
<!-- TOC -->

---

# Launch Harbor

> [!NOTE]
> I tried `include` but Harbor needs `sudo` whereas openstudiolandscapes does not. 
> This lead to problems, hence, launch them separately.
> ```shell
> include:  
>   - path:  
>     - ../.landscapes/.harbor/bin/docker-compose.yml
> ```

## nox

### up

```shell
nox --session harbor_up
```

#### detached

```shell
nox --session harbor_up_detach
```

### down

```shell
nox --session harbor_down
```

## Web Interface

[http://localhost:80]()
