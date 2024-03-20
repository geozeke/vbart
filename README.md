# vbart

<img
src="https://drive.google.com/uc?export=view&id=1H04KVAA3ohH_dLXIrC0bXuJXDn3VutKc"
alt = "Dinobox logo" width="120"/>

## Volume Backup And Restoration Tool for Docker

Why is backing up named docker volumes so hard? There's an
[extension][def] for Docker Desktop, but I just want a simple, easy to
use, command-line tool that allows me to backup and restore my named
docker volumes.

That's what vbart does.

All backups are stored in compressed (xz) tar archives. With vbart you
can:

1. Backup a single named volume.
2. Backup all active named volumes on your host.
3. Backup just the volumes you list in a separate file.
4. Restore a single backup to a named volume.

Once you create a backup, you can copy it off-host, install it on
another machine, share with friends, etc.

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

### Backup a single volume

```shell
vbart backup volume
```

For example, to backup a named volume called `mysql_db`, use:

```shell
vbart backup mysql_db
```

vbart will then create a backup file in your current working directory
named:

```text
YYYYMMDD-mysql_db-backup.xz
```

### Backup multiple volumes

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
YYYYMMDD-{volume}-backup.xz
```

### Restore a single volume

```shell
vbart restore backup_file volume_name
```

The first argument (`backup_file`) is the compressed tar archive you
created when you made a backup. The file should have a `.xz` extension.

The second argument (`volume_name`) is the named volume to create from
the backup. If the named volume already exists, vbart will terminate
with no action. Otherwise, a new empty volume will be created with the
given name and the backup will be restored to that volume.

[def]: https://hub.docker.com/extensions/docker/volumes-backup-extension
[def2]: https://pipx.pypa.io/stable/
