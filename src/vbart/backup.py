"""Perform single volume backup."""

import argparse
import sys

import docker  # type:ignore
from docker import errors

from vbart.classes import Labels
from vbart.utilities import backup_one_volume
from vbart.utilities import verify_utility_image


def task_runner(args: argparse.Namespace) -> None:
    """Backup a single named docker volume.

    Parameters
    ----------
    args : Namespace
        Command line arguments.
    """
    verify_utility_image()
    client = docker.from_env()

    try:
        client.volumes.get(args.volume_name)
        msg = f'Backing up volume "{args.volume_name}"'
        labels = Labels(msg)
    except errors.NotFound:
        print(f'Volume "{args.volume_name}" not found.')
        sys.exit(1)

    labels.next()
    print(backup_one_volume(args.volume_name))

    return


if __name__ == "__main__":
    pass
