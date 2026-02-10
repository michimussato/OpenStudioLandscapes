<!-- TOC -->
* [Rez vs. Spack](#rez-vs-spack)
  * [Rez](#rez)
  * [Spack](#spack)
<!-- TOC -->

---

# Rez vs. Spack

## Rez

- https://github.com/AcademySoftwareFoundation/rez
- https://rez.readthedocs.io/en/stable/index.html
- https://groups.google.com/g/rez-config/c/SHxFagCLWCc?pli=1

How to execute `rez` from containers that would need it?
How to execute `rez` from within pre-made containers?
- We must not grant access to `/var/run/docker.sock` to all containers: security issues

Can we install `rez` to a bind volume and mount it in all containers?
- add `rez` to `PATH`
- do we need the Python version that was used to install `rez` in all containers?

## Spack

- https://dev.to/chadrik/using-spack-to-build-the-vfx-refence-platform-5788
- https://spack.io/
- https://github.com/spack/spack
- https://spack.readthedocs.io/en/latest/
- https://hub.docker.com/u/spack
