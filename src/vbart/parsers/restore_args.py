"""Backup argparser."""

from argparse import FileType
from argparse import _SubParsersAction

COMMAND_NAME = "restore"


def load_command_args(sp: _SubParsersAction) -> None:
    """Assemble the argument parser."""
    msg = """Restore a single backup into a named docker volume."""
    parser = sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description=msg,
    )

    # Backup file.
    msg = """The backup file (.xz) to be restored."""
    parser.add_argument(
        "backup_file",
        type=FileType("rb"),
        help=msg,
    )

    # Volume name
    msg = """The named volume to create from the backup. If the named
    volume already exists, vbart will terminate with no action.
    Otherwise, a new empty volume will be created with the given name
    and the backup will be restored to that volume."""
    parser.add_argument(
        "volume_name",
        type=str,
        help=msg,
    )

    return
