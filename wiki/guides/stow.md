<!-- TOC -->
* [stow for Multiple .env Files](#stow-for-multiple-env-files)
  * [Requirements](#requirements)
  * [Set Up](#set-up)
  * [Usage](#usage)
    * [Simulate (aka. Dry Run)](#simulate-aka-dry-run)
    * [Verbosity](#verbosity)
    * [stow .env for Client_A](#stow-env-for-client_a)
    * [stow .env for Client_B](#stow-env-for-client_b)
<!-- TOC -->

---

# stow for Multiple .env Files

## Requirements

- `git`
- `stow`

## Set Up

Next to your OpenStudioLandscapes git repository,
create a new repository, say `stow`, on your hard drive.

1. For example: `cd ~/git/repos`
2. `mkdir stow`
3. `cd stow`
4. `git init --initial-branch=main`

```shell
$ ls -al ~/git/repos
drwxr-xr-x 39 michael michael 4096 Sep 20 10:31 .
drwxr-xr-x  4 michael michael 4096 Mar 11  2025 ..
[...]
drwxr-xr-x 24 michael michael 4096 Sep 22 11:38 OpenStudioLandscapes
[...]
drwxr-xr-x 19 michael michael 4096 Sep 22 11:07 stow
[...]
```

Now go ahead and create, say, an
`OpenStudioLandscapes` package:

1. `mkdir -p ~/git/repos/stow/OpenStudioLandscapes`

Then, you can create a nested (sub-) package for each `.env` file
that you intend to use. For example, you have a `Client_A` 
and a `Client_B` that you want to be able to create custom
Lanscapes for - each of which with different environments of 
course.

1. `mkdir -p ~/git/repos/stow/OpenStudioLandscapes/Client_A`
2. `mkdir -p ~/git/repos/stow/OpenStudioLandscapes/Client_B`

Next, copy/paste existing `.env` files into these sub-packages or
create them:

1. `touch ~/git/repos/stow/OpenStudioLandscapes/Client_A/.env`
2. `touch ~/git/repos/stow/OpenStudioLandscapes/Client_B/.env`

These new files being part of a version controlled Git 
repo, we can start tracking and commit them:

1. `git -C ~/git/repos/stow add *.env`
2. `git -C ~/git/repos/stow commit -m "some useful info here"`

That's the basic set up.

## Usage

### Simulate (aka. Dry Run)

In order to view the `stow` actions without actually
change anything to the system, you can use the
`--simulate` flag.

### Verbosity

In this guide, I use the `-vvv` flag for extended
verbosity but you can just drop it in case there is
too much going on for you.

### stow .env for Client_A

```shell
stow --override .env --dir ~/git/repos/stow/env/OpenStudioLandscapes --target ~/git/repos/OpenStudioLandscapes --stow Client_A -vvv
stow dir is /home/michael/git/repos/stow/env/OpenStudioLandscapes
stow dir path relative to target /home/michael/git/repos/OpenStudioLandscapes is ../stow/env/OpenStudioLandscapes
Planning stow of: Client_A ...
cwd now /home/michael/git/repos/OpenStudioLandscapes
Planning stow of package Client_A...
Stowing contents of ../stow/env/OpenStudioLandscapes / Client_A / . (cwd=~/git/repos/OpenStudioLandscapes)
Stowing entry ../stow/env/OpenStudioLandscapes / Client_A / .env
    level of .env is 0
LINK: .env => ../stow/env/OpenStudioLandscapes/Client_A/.env
Planning stow of package Client_A... done
cwd restored to /home/michael/git/repos/OpenStudioLandscapes
Processing tasks...
cwd now /home/michael/git/repos/OpenStudioLandscapes
cwd restored to /home/michael/git/repos/OpenStudioLandscapes
Processing tasks... don
```

### stow .env for Client_B

```shell
stow --override .env --dir ~/git/repos/stow/env/OpenStudioLandscapes --target ~/git/repos/OpenStudioLandscapes --stow Client_B -vvv
stow dir is /home/michael/git/repos/stow/env/OpenStudioLandscapes
stow dir path relative to target /home/michael/git/repos/OpenStudioLandscapes is ../stow/env/OpenStudioLandscapes
Planning stow of: Client_B ...
cwd now /home/michael/git/repos/OpenStudioLandscapes
Planning stow of package Client_B...
Stowing contents of ../stow/env/OpenStudioLandscapes / Client_B / . (cwd=~/git/repos/OpenStudioLandscapes)
Stowing entry ../stow/env/OpenStudioLandscapes / Client_B / .env
    level of .env is 0
LINK: .env => ../stow/env/OpenStudioLandscapes/Client_B/.env
Planning stow of package Client_B... done
cwd restored to /home/michael/git/repos/OpenStudioLandscapes
Processing tasks...
cwd now /home/michael/git/repos/OpenStudioLandscapes
cwd restored to /home/michael/git/repos/OpenStudioLandscapes
Processing tasks... don
```
