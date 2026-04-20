from __future__ import annotations

from datetime import datetime

import pytest
from docker import errors

from tests.conftest import FakeClient
from tests.conftest import FakeContainers
from tests.conftest import FakeImages
from tests.conftest import FakeSavedImage
from vbart.constants import BASE_IMAGE
from vbart.constants import DOCKERFILE_PATH
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
    monkeypatch.setattr(utilities.docker, "from_env", lambda: client)

    utilities.verify_utility_image()

    assert client.images.build_calls == []
    assert client.images.remove_calls == []


def test_verify_utility_image_builds_and_flattens_helper_image(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
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
    monkeypatch.setattr(utilities.docker, "from_env", lambda: client)

    utilities.verify_utility_image()

    assert images.build_calls == [
        {
            "path": str(DOCKERFILE_PATH),
            "tag": f"{UTILITY_IMAGE}:latest",
            "nocache": True,
            "rm": True,
        }
    ]
    assert images.remove_calls == [UTILITY_IMAGE]
    assert images.load_calls == [b"chunk1chunk2"]
    assert capsys.readouterr().out == "Building utility image (this is a one-time operation)...Done\n"


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
    monkeypatch.setattr(utilities.docker, "from_env", lambda: client)

    utilities.verify_utility_image()

    assert images.remove_calls == [UTILITY_IMAGE, BASE_IMAGE]


def test_backup_one_volume_builds_expected_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(containers=FakeContainers())
    monkeypatch.setattr(utilities.docker, "from_env", lambda: client)
    monkeypatch.setattr(utilities, "dt", FrozenDateTime)

    result = utilities.backup_one_volume("mysql_db")

    assert result == PASS
    run_call = client.containers.run_calls[0]
    assert run_call["command"] == "tar cavf /backup/20260420-mysql_db-backup.xz /recover"
    assert run_call["image"] == UTILITY_IMAGE
    assert run_call["volumes"]["mysql_db"]["bind"] == "/recover"
    assert run_call["volumes"][utilities.Path(".").absolute()]["bind"] == "/backup"


def test_backup_one_volume_returns_fail_on_container_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = FakeClient(
        containers=FakeContainers(
            run_side_effect=errors.ContainerError(None, 1, "cmd", "img", "stderr"),
        ),
    )
    monkeypatch.setattr(utilities.docker, "from_env", lambda: client)
    monkeypatch.setattr(utilities, "dt", FrozenDateTime)

    result = utilities.backup_one_volume("mysql_db")

    assert result == utilities.FAIL
