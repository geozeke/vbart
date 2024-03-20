"""Backup argparser."""

from argparse import _SubParsersAction

COMMAND_NAME = "refresh"


def load_command_args(sp: _SubParsersAction) -> None:
    """Assemble the argument parser."""
    msg = """When you run vbart for the first time it creates a small
    (alpine-based) docker image to perform the actual backups. This
    image is called "vbart_utility". This command will delete the image,
    causing it to be recreated the next time you run vbart."""
    sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description=msg,
    )

    return
