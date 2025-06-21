# Table Of Contents

<!-- TOC -->
* [Table Of Contents](#table-of-contents)
* [Terminology](#terminology)
<!-- TOC -->

---

# Terminology

| **Term**            | **Explanation**                                                                                                                                                                                                                        |     |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----|
| **Engine**          | The Engine is the OpenStudioLandscapes core which is mostly based on Docker and Dagster. The core itself provides pre and post steps as well as Feature discovery for the intermediate steps.                                          |     |
| **Landscape**       | A Landscape is an arbitrary composition of services.                                                                                                                                                                                   |     |
| **Feature**         | A Feature is a discoverable extension (module) for OpenStudioLandscapes. A Landscape is made of one or more Features.                                                                                                                  |     |
| **Registry**        | Registry is a repository where `docker` can push to and pull from. OpenStudioLandscapes relies on a local Harbor installation as its registry.                                                                                         |     |
| **Compose Context** | A Landscape can be broken up into multiple Compose Contexts. For example, a render client will run on a different machine than the render manager - they are part of the same Langscape but belong to separate docker compose files.   |     |
| **Landscape Map**   | [docker-compose-graph](#docker-compose-graph) is a `pip` installable package to turn `docker-compose.yaml` files into Graphviz diagrams, which, in turn, is a Landscape Map.                                                           |     |
| **Feature Config**  | As the name states, this is the Feature configuration. You can assign different Feature Configs to a single Feature - i.e. you can run a Deadline instance that listens on port 8877 and another one that listens on a different port. |     |
