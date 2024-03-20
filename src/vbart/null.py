"""Taskrunner for no command.

This will be the default command, which reminds the user how to use the
program, then exits.
"""

import argparse


def task_runner(args: argparse.Namespace) -> None:
    """Print reminder message and exit."""
    print("run 'vbart -h' for help.")
    return
