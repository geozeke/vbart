from __future__ import annotations

import importlib
import importlib.metadata
import sys
from types import SimpleNamespace

import pytest


def load_app_module(monkeypatch: pytest.MonkeyPatch):
    sys.modules.pop("vbart.app", None)
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "0.test")
    return importlib.import_module("vbart.app")


def test_main_exits_when_docker_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    app = load_app_module(monkeypatch)
    monkeypatch.setattr(app.shutil, "which", lambda name: None)

    with pytest.raises(SystemExit) as exc:
        app.main()

    assert exc.value.code == 1
    assert "You must have docker installed to use vbart." in capsys.readouterr().out


def test_main_dispatches_selected_command(monkeypatch: pytest.MonkeyPatch) -> None:
    app = load_app_module(monkeypatch)
    monkeypatch.setattr(app.shutil, "which", lambda name: "/usr/bin/docker")
    monkeypatch.setattr(
        app,
        "collect_parsers",
        lambda start: [
            "vbart.parsers.backup_args",
            "vbart.parsers.restore_args",
        ],
    )
    called: dict[str, object] = {}

    def load_backup_args(subparsers) -> None:
        parser = subparsers.add_parser("backup")
        parser.add_argument("volume_name")

    parser_module = SimpleNamespace(load_command_args=load_backup_args)
    restore_module = SimpleNamespace(load_command_args=lambda sp: sp.add_parser("restore"))

    def task_runner(args) -> None:
        called["cmd"] = args.cmd
        called["volume_name"] = args.volume_name

    command_module = SimpleNamespace(task_runner=task_runner)

    def fake_import_module(name: str):
        mapping = {
            "vbart.parsers.backup_args": parser_module,
            "vbart.parsers.restore_args": restore_module,
            "vbart.backup": command_module,
        }
        return mapping[name]

    monkeypatch.setattr(app.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(sys, "argv", ["vbart", "backup", "mysql_db"])

    app.main()

    assert called == {"cmd": "backup", "volume_name": "mysql_db"}


def test_main_dispatches_null_module_without_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = load_app_module(monkeypatch)
    monkeypatch.setattr(app.shutil, "which", lambda name: "/usr/bin/docker")
    monkeypatch.setattr(
        app,
        "collect_parsers",
        lambda start: [
            "vbart.parsers.backup_args",
            "vbart.parsers.restore_args",
        ],
    )
    called: dict[str, object] = {}

    def load_backup_args(subparsers) -> None:
        parser = subparsers.add_parser("backup")
        parser.add_argument("volume_name")

    parser_module = SimpleNamespace(load_command_args=load_backup_args)
    restore_module = SimpleNamespace(load_command_args=lambda sp: sp.add_parser("restore"))
    null_module = SimpleNamespace(task_runner=lambda args: called.setdefault("cmd", args.cmd))

    def fake_import_module(name: str):
        mapping = {
            "vbart.parsers.backup_args": parser_module,
            "vbart.parsers.restore_args": restore_module,
            "vbart.null": null_module,
        }
        return mapping[name]

    monkeypatch.setattr(app.importlib, "import_module", fake_import_module)
    monkeypatch.setattr(sys, "argv", ["vbart"])

    app.main()

    assert called == {"cmd": None}
