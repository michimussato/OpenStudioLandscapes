![logo128.png](media/images/logo128.png)

---

<!-- TOC -->
* [OpenStudioLandscapes](#openstudiolandscapes)
* [Community](#community)
* [Current Feature Statuses](#current-feature-statuses)
<!-- TOC -->

---

# OpenStudioLandscapes

Setup and launch custom production environments
with Render Farm, Production Tracking, Automation
and more - your 3D Animation
and VFX Pipeline backbone - with ease, independence
and scalability!
The way YOU want it!
YOU only!
Exactly!

An open source toolkit - a declarative build system - to
easily create reproducible production environments based
on your studio (even down to per production) needs: 
create Landscapes for production,
testing, debugging, development,
migration, DB restore etc.

![Overview](media/images/Overview.png)

No more black boxes.
No more path dependencies due to bad decisions
made in the past. Stay flexible and adaptable
with this modular and declarative system by reconfiguring
any production environment with ease:
- ✅ Easily add, edit, replace or remove services
- ✅ Clone (or modify and clone) entire production Landscapes for testing, debugging or development
- ✅ Code as source of truth:
  - ✅ Always stay on top of things with Landscape Maps and node tree representations of Python code
  - ✅ Limit manual documentation to a bare minimum
- ✅ `OpenStudioLandscapes` is (primarily) powered by [Dagster](https://github.com/dagster-io/) and [Docker](https://github.com/docker)
- ✅ Fully Python based
- ✅ Build your own studio automation
  - ✅ and share it (scripts, packages etc.) across Landscapes
- ✅ Do you like project based studio services?
  - ✅ No problem with OpenStudioLandscapes

This platform is aimed towards small to medium-sized
studios where only limited resources for Pipeline
Engineers and Technical Directors are available.
This system allows those studios to share a common
underlying system to build arbitrary pipeline tools
on top with the ability to share them among others
without sacrificing the technical freedom to implement
highly studio specific and individual solutions if needed.

The scope of this project are users with some technical skills with a
desire for a pre-made solution to set up their production
services and environments. OpenStudioLandscapes is therefore
a somewhat opinionated solution for working environments that
lack the fundamental skills and/or budgets to write a solution like
OpenStudioLandscapes by themselves while being flexible enough
for everyone *with* the technical skills to make their way through
configuring a Landscape or even writing their own OpenStudioLandscapes
Features for custom or proprietary services to fully fit their needs.

I guess this is a good starting point to open the project up to
the animation and VFX community to find out where (or where else) 
exactly the needs are to make sure small studios keep growing 
in a (from a technical perspective) healthy way without ending up
in a high "tech dept" dead end.

What problem does OpenStudioLandscapes solve?

What's separating the men from the boys is the production back bone.
Large studios spent years and years of man (and woman) hours and
millions of dollars to build robust automation to support their 
production while smaller ones are (in those regards - no matter
how recent and advanced the tools they use are) decades behind.
So, in one sense, OpenStudioLandscapes is a time machine by giving you 
the ability to jump a few years ahead of yourself by giving you a 
pre-made on-prem production environment at very little cost.

The second problem it is trying to solve is one that you (as a small
company) do not have **yet**. Ideally, before you start thinking about
automating processes, you want to have a robust underlying system. 
However, what usually happens is that
studios build their systems (again, while they are still small with no 
budget and/or understanding for professional automation) the other way around:
they write their small scripts and build everything else around and on top of that. This
almost inevitably leads to tech dept in the future after growth has happened - 
a house of cards built upside down. So, you wanna replace or remove your
old little script that you wrote 5 years ago which is being used in so many
places you can't even remember? There you have it. Better don't touch it. Better
continue building your system around it. Right? Wrong! OpenStudioLandscapes
is here to change that by making sure your **future you** is not going to 
regret decisions of its **past you**!

Bear in mind: OpenStudioLandscapes is a young project.
There are still many items to implement, such as for example a release strategy.
I lack experience in many fields when it comes to software development. The documentation
is not in a shape I would like to see it in. So, before adding features and Features to 
OpenStudioLandscapes, I plan to work on stability, documentation and support. 
To avoid filling in the wrong gaps, I would like to mainly fill in those 
that are being asked for - and this is your part. Ask anything. Request anything.
Suggest anything. Anything that leads to a better experience - without hiccups and without
too much noise at the same time - from installation to usage. If your field of expertise
can improve this project, please step forward and jump on board!
Now, it's time to head over to the [Wiki](wiki/README.md)!

# Community

- [![YouTube](media/images/youtube-square-red-logo-15975.png)](https://youtube.com/@openstudiolandscapes)
- [![LinkedIn](media/images/linkedin-square-blue-logo-15978.png)](https://www.linkedin.com/company/106731439/)
  - [#OpenStudioLandscapes](https://www.linkedin.com/search/results/all/?keywords=%23openstudiolandscapes)
- [![Discord](media/images/discord-square-blue-logo-16000.png)](https://discord.com/invite/aYnJnaqE)

[//]: # (Icons by https://www.iconpacks.net/free-icon-pack/free-social-media-network-logos-icon-pack-197.html)

# Current Feature Statuses

| Feature                                                                                                                      | Public |
|------------------------------------------------------------------------------------------------------------------------------|--------|
| [OpenStudioLandscapes-Ayon](https://github.com/michimussato/OpenStudioLandscapes-Ayon)                                       | ✅      |
| [OpenStudioLandscapes-Dagster](https://github.com/michimussato/OpenStudioLandscapes-Dagster)                                 | ✅      |
| [OpenStudioLandscapes-Deadline-10-2](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2)                     | ❌      |
| [OpenStudioLandscapes-Deadline-10-2-Worker](https://github.com/michimussato/OpenStudioLandscapes-Deadline-10-2-Worker)       | ❌      |
| [OpenStudioLandscapes-filebrowser](https://github.com/michimussato/OpenStudioLandscapes-filebrowser)                         | ❌      |
| [OpenStudioLandscapes-Grafana](https://github.com/michimussato/OpenStudioLandscapes-Grafana)                                 | ❌      |
| [OpenStudioLandscapes-Kitsu](https://github.com/michimussato/OpenStudioLandscapes-Kitsu)                                     | ✅      |
| [OpenStudioLandscapes-LikeC4](https://github.com/michimussato/OpenStudioLandscapes-LikeC4)                                   | ❌      |
| [OpenStudioLandscapes-NukeRLM-8](https://github.com/michimussato/OpenStudioLandscapes-NukeRLM-8)                             | ❌      |
| [OpenStudioLandscapes-OpenCue](https://github.com/michimussato/OpenStudioLandscapes-OpenCue)                                 | ❌      |
| [OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20](https://github.com/michimussato/OpenStudioLandscapes-SESI-gcc-9-3-Houdini-20) | ❌      |
| [OpenStudioLandscapes-Syncthing](https://github.com/michimussato/OpenStudioLandscapes-Syncthing)                             | ❌      |
| [OpenStudioLandscapes-Watchtower](https://github.com/michimussato/OpenStudioLandscapes-Watchtower)                           | ❌      |
| [OpenStudioLandscapes-Template](https://github.com/michimussato/OpenStudioLandscapes-Template)                               | ❌      |
