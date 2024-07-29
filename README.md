# vbart

![GitHub](https://img.shields.io/github/license/geozeke/vbart)
![PyPI](https://img.shields.io/pypi/v/vbart)
![PyPI - Status](https://img.shields.io/pypi/status/vbart)
![GitHub last commit](https://img.shields.io/github/last-commit/geozeke/vbart)
![GitHub issues](https://img.shields.io/github/issues/geozeke/vbart)
![PyPI - Downloads](https://img.shields.io/pypi/dm/vbart)
![GitHub repo size](https://img.shields.io/github/repo-size/geozeke/vbart)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/vbart)

<br>

<img
src="https://lh3.googleusercontent.com/d/1H04KVAA3ohH_dLXIrC0bXuJXDn3VutKc"
alt = "Dinobox logo" width="120"/>

## Volume Backup And Restoration Tool for Docker

Why is backing up named docker volumes so hard? There's an
[extension][def] for Docker Desktop, but I just want a simple,
easy-to-use command line tool that allows me to backup and restore my
named docker volumes. That's what vbart does.

With vbart you can:

* Backup a single named volume.
* Backup all active named volumes on your host.
* Backup just the volumes you list in a separate file.
* Restore a single backup to a named volume.

All backups are stored in compressed (xz) tar archives. Once you create
a backup, you can copy it off-host, install it on another machine, share
with friends, etc.

### Installation

The preferred way to install vbart is with [pipx][def2]:

```shell
pipx install vbart
```

Alternatively, you can create a separate virtual environment and install
it the traditional way:

```shell
pip3 install vbart
```

### Usage

For an overview, run:

```shell
vbart -h
```

### Backup a Single Volume

```shell
vbart backup volume_name
```

For example, to backup a volume named `mysql_db`, use:

```shell
vbart backup mysql_db
```

vbart will then create a backup file in your current working directory
named:

```text
YYYYMMDD-mysql_db-backup.xz
```

### Backup Multiple Volumes

```shell
vbart backups [-v VOLUMES]
```

Note the plural command name (`backups` as opposed to `backup`).
`VOLUMES` is the optional name of a textfile that contains case
sensitive volume names (one per line) that you want to backup. Within
`VOLUMES` blank lines and lines beginning with `#` are ignored, so you
can comment the file if you wish.

If `VOLUMES` is not specified, all active docker volumes on the current
host are backed up. All volume backups are saved in the current working
directory and named as:

```text
YYYYMMDD-{volume_name}-backup.xz
```

### Restore a Single Volume

```shell
vbart restore backup_file volume_name
```

The first argument (`backup_file`) is the compressed tar archive you
created when you made a backup. The file must have a `.xz` extension.

The second argument (`volume_name`) is the named volume to create from
the backup. If the named volume already exists, vbart will terminate
with no action. Otherwise, a new empty volume will be created with the
given name and the backup will be restored to that volume.

### Refresh vbart

If vbart is interrupted during execution (e.g. hitting `Control+C`),
then there may be dangling docker containers that hang on to existing
volumes. Running the refresh command will clear those dangling
containers.

Also, when you run vbart for the first time it creates a small
(alpine-based) docker image to perform the actual backups. This image is
called `vbart_utility`. The refresh command also deletes the utility
image, causing it to be recreated the next time you run vbart.

To refresh vbart, use:

```shell
vbart refresh
```

[def]: https://hub.docker.com/extensions/docker/volumes-backup-extension
[def2]: https://pipx.pypa.io/stable/
