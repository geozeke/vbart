"""Argument parser for the ``backups`` command."""

from argparse import _SubParsersAction
from pathlib import Path

COMMAND_NAME = "backups"


def load_command_args(sp: _SubParsersAction) -> None:
    """Register command-line arguments for ``backups``."""
    msg = """Back up multiple named Docker volumes."""
    parser = sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description="Create compressed backup archives for multiple named Docker volumes.",
    )

    # Volume names.
    msg = """If no options are given, all named Docker volumes on the
    host will be backed up to the current directory. You can also
    specify a file containing individual volume names (one per line) and
    back up only those volumes. When processing a file of
    volume names, blank lines and lines beginning with '#' will be
    ignored. Each backup archive will be named:
    YYYYMMDD-{volume_name}-backup.xz"""
    parser.add_argument(
        "-v",
        "--volumes",
        type=Path,
        help=msg,
    )

    return
