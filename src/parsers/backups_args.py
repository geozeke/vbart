"""Backup argparser."""

from argparse import FileType
from argparse import _SubParsersAction

COMMAND_NAME = "backups"


def load_command_args(sp: _SubParsersAction) -> None:
    """Assemble the argument parser."""
    msg = """Backup multiple named docker volumes."""
    parser = sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description=msg,
    )

    # Volume names.
    msg = """If no options are given, all named docker volumes on the
    host will be backed up to the current directory. If desired, you can
    specify a file containing individual volume names (one per line) and
    only those volumes will be backed up. When processing a file of
    volume names, blank lines and lines beginning with '#' will be
    ignored. Each backup created will be named:
    YYYYMMDD-{volume_name}-backup.xz"""
    parser.add_argument(
        "-v",
        "--volumes",
        type=FileType("r"),
        help=msg,
    )

    return
