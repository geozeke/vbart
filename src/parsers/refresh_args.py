"""Backup argparser."""

from argparse import _SubParsersAction

COMMAND_NAME = "refresh"


def load_command_args(sp: _SubParsersAction) -> None:
    """Assemble the argument parser."""
    msg = """If vbart is interrupted during execution (e.g. hitting
    Control+C), then there may be dangling docker containers that hang
    on to existing volumes. Running the refresh command will clear those
    dangling containers. Also, when you run vbart for the first time, it
    creates a small (alpine-based) docker image to perform the actual
    backups. This image is called "vbart_utility". The refresh command
    also deletes the utility image, causing it to be recreated the next
    time you run vbart."""
    sp.add_parser(
        name=COMMAND_NAME,
        help=msg,
        description=msg,
    )

    return
