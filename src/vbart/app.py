#!/usr/bin/env python3

"""CLI entry point for vbart."""

import argparse
import docker  # type:ignore
import importlib
import sys
from importlib.metadata import version
from pathlib import Path
from types import ModuleType
from docker import errors

from vbart.constants import APP_NAME
from vbart.constants import ARG_PARSERS_BASE

# ======================================================================

__version__ = version("vbart")
COMMAND_ORDER = ["backup", "backups", "restore", "refresh"]


def collect_parsers(start: Path) -> list[str]:
    """Collect argument parser module names.

    Parameters
    ----------
    start : Path
        Directory containing the parser modules to import.

    Returns
    -------
    list[str]
        Fully qualified parser module names.
    """
    parser_names: list[str] = []
    for p in start.iterdir():
        if p.is_file() and p.name != "__init__.py":
            parser_names.append(f"{APP_NAME}.parsers.{p.stem}")
    return parser_names


def sort_parsers(parser_names: list[str]) -> list[str]:
    """Sort parser modules in the desired CLI display order."""
    order = {
        f"{APP_NAME}.parsers.{name}_args": index
        for index, name in enumerate(COMMAND_ORDER)
    }
    return sorted(
        parser_names,
        key=lambda name: (order.get(name, len(order)), name),
    )


def verify_docker_runtime() -> None:
    """Exit if Docker is unavailable through the Python SDK."""
    try:
        client = docker.from_env()
        client.ping()
    except (errors.DockerException, OSError):
        print("\nYou must have a working Docker runtime to use vbart.\n")
        sys.exit(1)


# ======================================================================


def main() -> None:
    """Parse CLI arguments and dispatch the selected command."""
    verify_docker_runtime()

    msg = """
    Back up and restore named Docker volumes.
    """
    epi = f"Version: {__version__}"
    parser = argparse.ArgumentParser(
        description=msg,
        epilog=epi,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{APP_NAME} {__version__}",
    )
    msg = "Run 'vbart COMMAND -h' for help on a specific command."
    subparsers = parser.add_subparsers(
        title="commands",
        dest="cmd",
        description=msg,
    )

    # Dynamically load argument subparsers.

    parser_names = sort_parsers(collect_parsers(ARG_PARSERS_BASE))

    mod: ModuleType | None = None
    for p_name in parser_names:
        mod = importlib.import_module(p_name)
        mod.load_command_args(subparsers)

    # Run the selected command. Python's argparse module guarantees that
    # we'll get either: (1) a valid command or (2) no command at all
    # (args.cmd == None). Given that, we can easily determine the
    # entered command.

    args = parser.parse_args()
    if args.cmd:
        mod = importlib.import_module(f"{APP_NAME}.{args.cmd}")
    else:
        mod = importlib.import_module(f"{APP_NAME}.null")
    mod.task_runner(args)

    return


if __name__ == "__main__":
    main()
