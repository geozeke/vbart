"""Argument parser for the ``restore`` command."""

from argparse import _SubParsersAction
from pathlib import Path

COMMAND_NAME = "restore"


def load_command_args(sp: _SubParsersAction) -> None:
    """Register command-line arguments for ``restore``."""
    msg = """Restore a single backup into a named Docker volume."""
    parser = sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description="Restore a backup archive into a newly created named Docker volume.",
    )

    # Backup file.
    msg = """The .xz backup archive to restore."""
    parser.add_argument(
        "backup_file",
        type=Path,
        help=msg,
    )

    # Volume name
    msg = """The destination volume name. If the volume already exists,
    vbart will exit without restoring. Otherwise, vbart will create a
    new empty volume with this name and restore the backup into it."""
    parser.add_argument(
        "volume_name",
        type=str,
        help=msg,
    )

    return
