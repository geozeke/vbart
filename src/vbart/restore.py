"""Command handler for restoring a Docker volume from a backup."""

import argparse
import shlex
import sys
from pathlib import Path

from docker import errors  # type:ignore

from vbart.classes import Labels
from vbart.compression import compression_from_path
from vbart.constants import FAIL
from vbart.constants import PASS
from vbart.constants import UTILITY_IMAGE
from vbart.runtime import get_docker_client
from vbart.runtime import normalize_bind_source
from vbart.utilities import verify_utility_image


def task_runner(args: argparse.Namespace) -> None:
    """Restore a backup archive to a Docker volume.

    Parameters
    ----------
    args : Namespace
        Parsed command-line arguments.
    """
    p = Path(args.backup_file)
    compression = compression_from_path(p)
    if not compression:
        print(f'Backup file "{p}" uses an unsupported compression format.')
        sys.exit(1)
    verify_utility_image()
    client = get_docker_client()

    # Check to see if the volume already exists. If so, report that and
    # exit. If it doesn't exist, create it.

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

    volume_map = {
        args.volume_name: {"bind": "/recover", "mode": "rw"},
        normalize_bind_source(p.parent): {"bind": "/backup", "mode": "rw"},
    }

    # Build the shell command to be run in the container

    shell_arg = shlex.quote(compression.restore_command(Path("/backup") / p.name))
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
