"""Backup argparser."""

from argparse import _SubParsersAction

COMMAND_NAME = "backup"


def load_command_args(sp: _SubParsersAction) -> None:
    """Assemble the argument parser."""
    msg = """Backup a single named docker volume."""
    parser = sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description=msg,
    )

    # Volume name.
    msg = """The named docker volume to be backed up. The backup file
    will be created in the current directory with the name:
    YYYYMMDD-{volume_name}-backup.xz"""
    parser.add_argument(
        "volume_name",
        type=str,
        help=msg,
    )

    return
