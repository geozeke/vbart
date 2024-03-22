"""Remove the vbart_utility image."""

import argparse

import docker  # type:ignore
from docker import errors

from vbart.constants import UTILITY_IMAGE


def task_runner(args: argparse.Namespace) -> None:
    """Purge any dangling containers and remove the vbart_utility image.

    If a backup is interrupted (e.g. cntl-C), then there may be dangling
    containers that are still hanging on to existing volumes. The
    refresh option purges those dangling containers.

    Parameters
    ----------
    args : Namespace
        Command line arguments.
    """
    client = docker.from_env()

    # Prune any dangling containers.

    filter = {"ancestor": f"{UTILITY_IMAGE}:latest"}
    dangling = client.containers.list(
        all=True,
        filters=filter,
    )

    for container in dangling:
        container.remove(force=True)  # type:ignore

    # Delete the utility image and appropriate dependency.

    try:
        client.images.get(UTILITY_IMAGE)
        client.images.remove(UTILITY_IMAGE)
    except errors.NotFound:
        print("No refresh needed. All good.")
        return

    if dangling:
        noun = "container" if len(dangling) == 1 else "containers"
        print(f"{len(dangling)} dangling {noun} removed.")
    print(f"The {UTILITY_IMAGE} image was deleted.")
    print(f"{UTILITY_IMAGE} will be recreated the next time you run vbart.")

    return


if __name__ == "__main__":
    pass
