"""Perform single volume backup."""

import argparse
import sys

import docker  # type:ignore
from docker import errors

from vbart.classes import Labels
from vbart.utilities import backup_one_volume
from vbart.utilities import clear
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
        client.volumes.get(args.volume)
        msg = f'Backing up volume "{args.volume}"'
        labels = Labels(msg)
    except errors.NotFound:
        print(f'Volume "{args.volume}" not found.')
        sys.exit(1)

    clear()
    labels.next()
    print(backup_one_volume(args.volume))

    return


if __name__ == "__main__":
    pass
