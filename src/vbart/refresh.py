"""Command handler for refreshing vbart helper resources."""

import argparse

import docker  # type:ignore
from docker import errors

from vbart.constants import UTILITY_IMAGE


def task_runner(args: argparse.Namespace) -> None:
    """Remove dangling containers and the ``vbart_utility`` image.

    If a backup is interrupted, for example by pressing ``Ctrl+C``,
    dangling containers may continue to reference existing volumes. This
    command removes those containers and deletes the helper image so it
    can be rebuilt on the next run.

    Parameters
    ----------
    args : Namespace
        Parsed command-line arguments.
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
