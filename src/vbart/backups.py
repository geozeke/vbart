"""Command handler for backing up multiple Docker volumes."""

import argparse
import textwrap

from vbart.classes import Labels
from vbart.runtime import get_docker_client
from vbart.utilities import backup_one_volume
from vbart.utilities import verify_utility_image


def task_runner(args: argparse.Namespace) -> None:
    """Back up multiple Docker volumes.

    Parameters
    ----------
    args : Namespace
        Parsed command-line arguments.
    """
    verify_utility_image()
    client = get_docker_client()
    active_names = [v.name for v in client.volumes.list()]  # type:ignore

    if args.volumes:
        print(f"Performing backups using {args.volumes.name}\n")
        custom_names = [
            t for
            token in args.volumes
            if (t := token.strip()) and (t[0] != "#")
        ]  # fmt: skip
        args.volumes.close()
        target_names = list(set(active_names).intersection(set(custom_names)))
    else:
        print("Backing up all active Docker volumes\n")
        target_names = active_names.copy()
    target_names.sort()

    if target_names:
        label_list = [f'Backing up volume "{name}"' for name in target_names]
        labels = Labels("\n".join(label_list))
        for name in target_names:
            labels.next()
            print(backup_one_volume(name))
    else:
        if args.volumes:
            msg = f"""None of the volume names listed in
            {args.volumes.name} are currently showing up as active
            Docker volumes."""
            print(f"{textwrap.fill(text=' '.join(msg.split()),width=60)}")
        else:
            print("No active Docker volumes found.")

    return


if __name__ == "__main__":
    pass
