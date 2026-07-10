from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import FakeClient
from vbart import runtime


def test_normalize_bind_source_preserves_posix_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(runtime.sys, "platform", "linux")

    assert runtime.normalize_bind_source(tmp_path) == str(tmp_path.resolve())


def test_normalize_bind_source_converts_windows_separators(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime.sys, "platform", "win32")

    class FakeResolvedPath:
        def resolve(self) -> str:
            return r"C:\Users\me\backups"

    assert runtime.normalize_bind_source(FakeResolvedPath()) == "C:/Users/me/backups"  # type: ignore[arg-type]


def test_validate_runtime_mode_allows_linux_containers_on_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime.sys, "platform", "win32")

    runtime.validate_runtime_mode(FakeClient(info_data={"OSType": "linux"}))


def test_validate_runtime_mode_rejects_windows_containers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime.sys, "platform", "win32")

    with pytest.raises(runtime.UnsupportedRuntimeError) as exc:
        runtime.validate_runtime_mode(FakeClient(info_data={"OSType": "windows"}))

    assert "Linux containers" in str(exc.value)


def test_get_docker_client_validates_runtime(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(info_data={"OSType": "linux"})
    from_env_calls: list[dict[str, object]] = []

    def from_env(**kwargs: object) -> FakeClient:
        from_env_calls.append(kwargs)
        return client

    monkeypatch.setattr(runtime.sys, "platform", "win32")
    monkeypatch.setattr(runtime.docker, "from_env", from_env)

    result = runtime.get_docker_client()

    assert result is client
    assert from_env_calls == [{"use_context": False}]
    assert client.ping_calls == 1
