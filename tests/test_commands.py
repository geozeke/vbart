from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import Any
from typing import cast

import pytest
from docker import errors

from tests.conftest import FakeClient
from tests.conftest import FakeContainer
from tests.conftest import FakeContainers
from tests.conftest import FakeImages
from tests.conftest import FakeVolumes
from vbart import backup
from vbart import backups
from vbart import null
from vbart import refresh
from vbart import restore
from vbart.constants import UTILITY_IMAGE


def test_backup_task_runner_backs_up_existing_volume(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(volumes=FakeVolumes(existing_names=["mysql_db"]))
    monkeypatch.setattr(backup, "verify_utility_image", lambda: None)
    monkeypatch.setattr(backup, "get_docker_client", lambda: client)
    monkeypatch.setattr(backup, "backup_one_volume", lambda name: "RESULT")

    backup.task_runner(Namespace(volume_name="mysql_db"))

    assert 'Backing up volume "mysql_db"' in capsys.readouterr().out


def test_backup_task_runner_exits_for_missing_volume(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(volumes=FakeVolumes(existing_names=[]))
    monkeypatch.setattr(backup, "verify_utility_image", lambda: None)
    monkeypatch.setattr(backup, "get_docker_client", lambda: client)

    with pytest.raises(SystemExit) as exc:
        backup.task_runner(Namespace(volume_name="missing"))

    assert exc.value.code == 1
    assert 'Volume "missing" not found.' in capsys.readouterr().out


def test_backups_task_runner_uses_sorted_active_volumes(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(volumes=FakeVolumes(existing_names=["zeta", "alpha"]))
    backed_up: list[str] = []
    monkeypatch.setattr(backups, "verify_utility_image", lambda: None)
    monkeypatch.setattr(backups, "get_docker_client", lambda: client)
    monkeypatch.setattr(
        backups,
        "backup_one_volume",
        lambda name: backed_up.append(name) or "OK",
    )

    backups.task_runner(Namespace(volumes=None))

    assert backed_up == ["alpha", "zeta"]
    assert "Backing up all active Docker volumes" in capsys.readouterr().out


def test_backups_task_runner_filters_from_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(volumes=FakeVolumes(existing_names=["db", "cache"]))
    backed_up: list[str] = []
    volume_list = tmp_path / "volumes.txt"
    volume_list.write_text("# comment\ndb\nmissing\n", encoding="utf-8")
    monkeypatch.setattr(backups, "verify_utility_image", lambda: None)
    monkeypatch.setattr(backups, "get_docker_client", lambda: client)
    monkeypatch.setattr(
        backups,
        "backup_one_volume",
        lambda name: backed_up.append(name) or "OK",
    )

    backups.task_runner(Namespace(volumes=volume_list))

    assert backed_up == ["db"]
    assert f"Performing backups using {volume_list}" in capsys.readouterr().out


def test_backups_task_runner_reports_empty_match(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(volumes=FakeVolumes(existing_names=["db"]))
    volume_list = tmp_path / "volumes.txt"
    volume_list.write_text("cache\n", encoding="utf-8")
    monkeypatch.setattr(backups, "verify_utility_image", lambda: None)
    monkeypatch.setattr(backups, "get_docker_client", lambda: client)

    backups.task_runner(Namespace(volumes=volume_list))

    assert "currently showing up as active Docker volumes" in capsys.readouterr().out


def test_restore_task_runner_exits_when_target_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(volumes=FakeVolumes(existing_names=["restored"]))
    backup_file = tmp_path / "backup.xz"
    backup_file.write_bytes(b"data")
    monkeypatch.setattr(restore, "verify_utility_image", lambda: None)
    monkeypatch.setattr(restore, "get_docker_client", lambda: client)

    with pytest.raises(SystemExit) as exc:
        restore.task_runner(Namespace(backup_file=backup_file, volume_name="restored"))

    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert 'Volume "restored" already exists.' in out
    assert "No restoration performed." in out


def test_restore_task_runner_restores_new_volume(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(
        volumes=FakeVolumes(existing_names=[]), containers=FakeContainers()
    )
    backup_file = tmp_path / "backup.xz"
    backup_file.write_bytes(b"data")
    monkeypatch.setattr(restore, "verify_utility_image", lambda: None)
    monkeypatch.setattr(restore, "get_docker_client", lambda: client)

    restore.task_runner(Namespace(backup_file=backup_file, volume_name="restored"))

    assert client.volumes.create_calls == ["restored"]
    run_call = client.containers.run_calls[0]
    assert run_call["image"] == UTILITY_IMAGE
    assert (
        run_call["command"]
        == 'sh -c "cd /recover && tar xvf /backup/backup.xz --strip 1"'
    )
    assert run_call["volumes"]["restored"]["bind"] == "/recover"
    backup_root = restore.normalize_bind_source(tmp_path)
    assert run_call["volumes"][backup_root]["bind"] == "/backup"
    assert capsys.readouterr().out.endswith("✅\n")


def test_restore_task_runner_removes_created_volume_on_invalid_backup(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(
        volumes=FakeVolumes(existing_names=[]),
        containers=FakeContainers(
            run_side_effect=errors.ContainerError(
                cast(Any, object()),
                1,
                "cmd",
                "img",
                "stderr",
            ),
        ),
    )
    backup_file = tmp_path / "backup.xz"
    backup_file.write_bytes(b"data")
    monkeypatch.setattr(restore, "verify_utility_image", lambda: None)
    monkeypatch.setattr(restore, "get_docker_client", lambda: client)

    with pytest.raises(SystemExit) as exc:
        restore.task_runner(Namespace(backup_file=backup_file, volume_name="restored"))

    assert exc.value.code == 1
    created_volume = client.volumes.by_name["restored"]
    assert created_volume.remove_calls == [{}]
    assert "Invalid backup file provided. Unable to restore." in capsys.readouterr().out


def test_refresh_task_runner_removes_dangling_containers_and_image(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    containers = [FakeContainer(), FakeContainer()]
    client = FakeClient(
        images=FakeImages(existing={UTILITY_IMAGE: object()}),
        containers=FakeContainers(listed=containers),
    )
    monkeypatch.setattr(refresh, "get_docker_client", lambda: client)

    refresh.task_runner(Namespace())

    assert client.containers.list_calls == [
        {"all": True, "filters": {"ancestor": f"{UTILITY_IMAGE}:latest"}}
    ]
    assert [c.remove_calls for c in containers] == [
        [{"force": True}],
        [{"force": True}],
    ]
    assert client.images.remove_calls == [UTILITY_IMAGE]
    assert "2 dangling containers removed." in capsys.readouterr().out


def test_refresh_task_runner_reports_when_no_refresh_is_needed(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    client = FakeClient(images=FakeImages(existing={}))
    monkeypatch.setattr(refresh, "get_docker_client", lambda: client)

    refresh.task_runner(Namespace())

    assert capsys.readouterr().out.strip() == "No refresh needed. All good."


def test_null_task_runner_prints_help_hint(
    capsys: pytest.CaptureFixture[str],
) -> None:
    null.task_runner(Namespace())

    assert capsys.readouterr().out.strip() == "run 'vbart -h' for help."
