"""Perform volume restoration."""

import argparse
import sys
from pathlib import Path

import docker  # type:ignore
from docker import errors

from vbart.classes import Labels
from vbart.constants import FAIL
from vbart.constants import PASS
from vbart.constants import UTILITY_IMAGE
from vbart.utilities import verify_utility_image


def task_runner(args: argparse.Namespace) -> None:
    """Restore a backup to a docker volume.

    Parameters
    ----------
    args : Namespace
        Command line arguments.
    """
    verify_utility_image()
    client = docker.from_env()

    # Check to see if the volume already exists. If so, report that and
    # exit. If it doesn't exist, create it. Also, close the backup file
    # - when it comes time to run the container, we only need the name.

    args.backup_file.close()
    try:
        client.volumes.get(args.volume_name)
        print(f'Volume "{args.volume_name}" already exists.')
        print("No restoration performed.")
        sys.exit(0)
    except errors.NotFound:
        msg = f'Restoring backup to volume "{args.volume_name}"'
        volume = client.volumes.create(args.volume_name)
        labels = Labels(msg)

    # Build volume map.

    p = Path(args.backup_file.name)
    volume_map = {
        args.volume_name: {"bind": "/recover", "mode": "rw"},
        p.parent.absolute(): {"bind": "/backup", "mode": "rw"},
    }

    # Build the shell command to be run in the container

    shell_arg = f'"cd /recover && tar xvf /backup/{p.name} --strip 1"'
    shell_cmd = f"sh -c {shell_arg}"

    # Run the container and extract the backup.

    try:
        labels.next()
        client.containers.run(
            image=UTILITY_IMAGE,
            command=shell_cmd,
            remove=True,
            volumes=volume_map,  # type:ignore
        )
        print(PASS)
    except errors.ContainerError:
        print(FAIL)
        print("\nInvalid backup file provided. Unable to restore.")
        volume.remove()  # type:ignore
        sys.exit(1)

    return


if __name__ == "__main__":
    pass
