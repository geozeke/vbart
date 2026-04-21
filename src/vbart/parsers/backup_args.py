"""Argument parser for the ``backup`` command."""

from argparse import _SubParsersAction

COMMAND_NAME = "backup"


def load_command_args(sp: _SubParsersAction) -> None:
    """Register command-line arguments for ``backup``."""
    msg = """Back up a single named Docker volume."""
    parser = sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description="Create a compressed backup archive for one named Docker volume.",
    )

    # Volume name.
    msg = """The named Docker volume to back up. The backup archive
    will be created in the current directory with the name:
    YYYYMMDD-{volume_name}-backup.xz"""
    parser.add_argument(
        "volume_name",
        type=str,
        help=msg,
    )

    return
