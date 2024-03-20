"""Remove the vbart_utility image."""

import argparse

import docker  # type:ignore
from docker import errors

from vbart.constants import UTILITY_IMAGE


def task_runner(args: argparse.Namespace) -> None:
    """Remove the vbart_utility image.

    Parameters
    ----------
    args : Namespace
        Command line arguments.
    """
    client = docker.from_env()

    try:
        client.images.get(UTILITY_IMAGE)
        client.images.remove(UTILITY_IMAGE)
    except errors.NotFound:
        pass

    print(f"The {UTILITY_IMAGE} image was deleted.")
    print("A fresh one will be created the next time you run vbart.")

    return


if __name__ == "__main__":
    pass
