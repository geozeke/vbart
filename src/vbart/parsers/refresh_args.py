"""Backup argparser."""

from argparse import _SubParsersAction

COMMAND_NAME = "refresh"


def load_command_args(sp: _SubParsersAction) -> None:
    """Assemble the argument parser."""
    msg = """Remove dangling vbart containers and recreate the helper image on the next run."""
    sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description="""Remove dangling vbart containers that may remain
        after an interrupted run and delete the vbart_utility helper
        image so it is rebuilt automatically the next time you use
        vbart.""",
    )

    return
