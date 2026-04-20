"""Fallback handler when no subcommand is provided.

This module prints a short usage reminder and exits.
"""

import argparse


def task_runner(args: argparse.Namespace) -> None:
    """Print a usage reminder."""
    print("run 'vbart -h' for help.")
    return
