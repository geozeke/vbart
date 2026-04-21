from __future__ import annotations

import argparse
from pathlib import Path

from vbart.parsers import backup_args
from vbart.parsers import backups_args
from vbart.parsers import refresh_args
from vbart.parsers import restore_args


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    return parser


def test_backup_parser_registers_volume_name() -> None:
    parser = build_parser()
    subparsers = parser.add_subparsers(dest="cmd")
    backup_args.load_command_args(subparsers)

    args = parser.parse_args(["backup", "mysql_db"])

    assert args.cmd == "backup"
    assert args.volume_name == "mysql_db"


def test_backups_parser_registers_optional_volume_file(tmp_path: Path) -> None:
    parser = build_parser()
    subparsers = parser.add_subparsers(dest="cmd")
    backups_args.load_command_args(subparsers)
    volume_list = tmp_path / "volumes.txt"
    volume_list.write_text("db\n", encoding="utf-8")

    args = parser.parse_args(["backups", "-v", str(volume_list)])

    assert args.cmd == "backups"
    assert args.volumes == volume_list


def test_restore_parser_registers_backup_file_and_volume_name(tmp_path: Path) -> None:
    parser = build_parser()
    subparsers = parser.add_subparsers(dest="cmd")
    restore_args.load_command_args(subparsers)
    backup_file = tmp_path / "backup.xz"
    backup_file.write_bytes(b"data")

    args = parser.parse_args(["restore", str(backup_file), "mysql_db"])

    assert args.cmd == "restore"
    assert args.backup_file == backup_file
    assert args.volume_name == "mysql_db"


def test_refresh_parser_registers_command_without_args() -> None:
    parser = build_parser()
    subparsers = parser.add_subparsers(dest="cmd")
    refresh_args.load_command_args(subparsers)

    args = parser.parse_args(["refresh"])

    assert args.cmd == "refresh"
