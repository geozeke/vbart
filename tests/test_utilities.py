from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
from typing import cast

import pytest
from docker import errors

from tests.conftest import FakeClient
from tests.conftest import FakeContainers
from tests.conftest import FakeImages
from tests.conftest import FakeSavedImage
from vbart.constants import BASE_IMAGE
from vbart.constants import HELPER_IMAGE_VERSION
from vbart.constants import HELPER_IMAGE_VERSION_LABEL
from vbart.constants import PASS
from vbart.constants import UTILITY_IMAGE
from vbart import utilities


class FrozenDateTime:
    @classmethod
    def now(cls) -> datetime:
        return datetime(2026, 4, 20, 9, 30, 0)


def test_verify_utility_image_returns_when_image_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(images=FakeImages(existing={UTILITY_IMAGE: FakeSavedImage()}))
    monkeypatch.setattr(utilities, "get_docker_client", lambda: client)

    utilities.verify_utility_image()

    assert client.images.build_calls == []
    assert client.images.remove_calls == []


def test_verify_utility_image_builds_and_flattens_helper_image(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    images = FakeImages(
        existing={
            BASE_IMAGE: object(),
            UTILITY_IMAGE: FakeSavedImage([b"chunk1", b"chunk2"]),
        },
    )
    client = FakeClient(images=images)
    first_lookup = {"done": False}

    def get(name: str):
        if name == UTILITY_IMAGE and not first_lookup["done"]:
            first_lookup["done"] = True
            raise errors.ImageNotFound("missing utility image")
        return images.existing[name]

    monkeypatch.setattr(images, "get", get)
    monkeypatch.setattr(utilities, "get_docker_client", lambda: client)
    monkeypatch.setattr(
        utilities,
        "render_helper_dockerfile",
        lambda: "FROM alpine:3.23\nRUN echo hello\n",
    )
    build_dir = tmp_path / "build-context"
    build_dir.mkdir()

    class FakeTemporaryDirectory:
        def __enter__(self) -> str:
            return str(build_dir)

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    monkeypatch.setattr(utilities.tf, "TemporaryDirectory", FakeTemporaryDirectory)

    utilities.verify_utility_image()

    build_call = images.build_calls[0]
    assert build_call["tag"] == f"{UTILITY_IMAGE}:latest"
    assert build_call["nocache"] is True
    assert build_call["rm"] is True
    dockerfile_path = build_dir / "Dockerfile"
    assert (
        dockerfile_path.read_text(encoding="utf-8")
        == "FROM alpine:3.23\nRUN echo hello\n"
    )
    assert images.remove_calls == [UTILITY_IMAGE]
    assert images.load_calls == [b"chunk1chunk2"]
    assert (
        capsys.readouterr().out
        == "Building utility image (this is a one-time operation)...Done\n"
    )


def test_verify_utility_image_rebuilds_stale_helper_image(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    images = FakeImages(
        existing={
            BASE_IMAGE: object(),
            UTILITY_IMAGE: FakeSavedImage(labels={}),
        },
    )
    client = FakeClient(images=images)
    monkeypatch.setattr(utilities, "get_docker_client", lambda: client)
    monkeypatch.setattr(
        utilities,
        "render_helper_dockerfile",
        lambda: "FROM alpine:3.23\n",
    )

    utilities.verify_utility_image()

    assert images.build_calls[0]["tag"] == f"{UTILITY_IMAGE}:latest"


def test_verify_utility_image_removes_pulled_base_image(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    images = FakeImages(existing={UTILITY_IMAGE: FakeSavedImage()})
    client = FakeClient(images=images)
    first_utility_lookup = {"done": False}

    def get(name: str):
        if name == UTILITY_IMAGE and not first_utility_lookup["done"]:
            first_utility_lookup["done"] = True
            raise errors.ImageNotFound("missing utility image")
        if name == BASE_IMAGE:
            raise errors.ImageNotFound("missing base image")
        return images.existing[name]

    monkeypatch.setattr(images, "get", get)
    monkeypatch.setattr(utilities, "get_docker_client", lambda: client)
    monkeypatch.setattr(
        utilities,
        "render_helper_dockerfile",
        lambda: "FROM alpine:3.23\n",
    )

    utilities.verify_utility_image()

    assert images.remove_calls == [UTILITY_IMAGE, BASE_IMAGE]


def test_render_helper_dockerfile_uses_base_image_constant() -> None:
    dockerfile = utilities.render_helper_dockerfile()

    assert dockerfile.startswith("FROM alpine:3.23\n")
    assert f'{HELPER_IMAGE_VERSION_LABEL}="{HELPER_IMAGE_VERSION}"' in dockerfile
    assert (
        "apk add --no-cache 7zip bzip2 bzip3 gzip tar unzip xz zip zstd" in dockerfile
    )


@pytest.mark.parametrize(
    ("compression", "suffix", "fragment"),
    [
        ("gzip", ".tar.gz", "gzip -c >"),
        ("xz", ".tar.xz", "xz -c >"),
        ("zstd", ".tar.zst", "zstd -c >"),
        ("bzip2", ".tar.bz2", "bzip2 -c >"),
        ("bzip3", ".tar.bz3", "bzip3 -c >"),
        ("7z", ".tar.7z", "7zz a"),
        ("zip", ".tar.zip", "zip -q"),
    ],
)
def test_backup_one_volume_builds_expected_command(
    monkeypatch: pytest.MonkeyPatch,
    compression: str,
    suffix: str,
    fragment: str,
) -> None:
    client = FakeClient(containers=FakeContainers())
    monkeypatch.setattr(utilities, "get_docker_client", lambda: client)
    monkeypatch.setattr(utilities, "dt", FrozenDateTime)

    result = utilities.backup_one_volume("mysql_db", compression)

    assert result == PASS
    run_call = client.containers.run_calls[0]
    command = run_call["command"]
    assert command.startswith("sh -c ")
    assert f"/backup/20260420-mysql_db-backup{suffix}" in command
    assert "tar -cf - /recover" in command
    assert fragment in command
    assert run_call["image"] == UTILITY_IMAGE
    assert run_call["volumes"]["mysql_db"]["bind"] == "/recover"
    backup_root = utilities.normalize_bind_source(utilities.Path("."))
    assert run_call["volumes"][backup_root]["bind"] == "/backup"


def test_backup_one_volume_returns_fail_on_container_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(
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
    monkeypatch.setattr(utilities, "get_docker_client", lambda: client)
    monkeypatch.setattr(utilities, "dt", FrozenDateTime)

    result = utilities.backup_one_volume("mysql_db")

    assert result == utilities.FAIL
