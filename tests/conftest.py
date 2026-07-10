from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from docker import errors

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from vbart.constants import HELPER_IMAGE_VERSION  # noqa: E402
from vbart.constants import HELPER_IMAGE_VERSION_LABEL  # noqa: E402


class FakeSavedImage:
    def __init__(
        self,
        chunks: list[bytes] | None = None,
        labels: dict[str, str] | None = None,
    ) -> None:
        self.chunks = chunks or [b"image-bytes"]
        self.attrs = {
            "Config": {
                "Labels": labels
                if labels is not None
                else {HELPER_IMAGE_VERSION_LABEL: HELPER_IMAGE_VERSION}
            }
        }

    def save(self, named: bool = True):  # noqa: FBT001, FBT002
        yield from self.chunks


class FakeImages:
    def __init__(self, existing: dict[str, Any] | None = None) -> None:
        self.existing = existing or {}
        self.build_calls: list[dict[str, Any]] = []
        self.remove_calls: list[str] = []
        self.load_calls: list[bytes] = []

    def get(self, name: str) -> Any:
        if name not in self.existing:
            raise errors.ImageNotFound("missing image")
        return self.existing[name]

    def build(self, **kwargs: Any) -> None:
        self.build_calls.append(kwargs)

    def remove(self, name: str) -> None:
        self.remove_calls.append(name)
        self.existing.pop(name, None)

    def load(self, payload: bytes) -> None:
        self.load_calls.append(payload)


class FakeVolume:
    def __init__(self, name: str) -> None:
        self.name = name
        self.remove_calls: list[dict[str, Any]] = []

    def remove(self, **kwargs: Any) -> None:
        self.remove_calls.append(kwargs)


class FakeVolumes:
    def __init__(self, existing_names: list[str] | None = None) -> None:
        self.by_name = {name: FakeVolume(name) for name in (existing_names or [])}
        self.create_calls: list[str] = []

    def get(self, name: str) -> FakeVolume:
        if name not in self.by_name:
            raise errors.NotFound("missing volume")
        return self.by_name[name]

    def list(self) -> list[FakeVolume]:
        return list(self.by_name.values())

    def create(self, name: str) -> FakeVolume:
        self.create_calls.append(name)
        volume = FakeVolume(name)
        self.by_name[name] = volume
        return volume


class FakeContainer:
    def __init__(self) -> None:
        self.remove_calls: list[dict[str, Any]] = []

    def remove(self, **kwargs: Any) -> None:
        self.remove_calls.append(kwargs)


class FakeContainers:
    def __init__(
        self,
        run_side_effect: Exception | None = None,
        listed: list[FakeContainer] | None = None,
    ) -> None:
        self.run_side_effect = run_side_effect
        self.run_calls: list[dict[str, Any]] = []
        self.list_calls: list[dict[str, Any]] = []
        self.listed = listed or []

    def run(self, **kwargs: Any) -> None:
        self.run_calls.append(kwargs)
        if self.run_side_effect is not None:
            raise self.run_side_effect

    def list(self, **kwargs: Any) -> list[FakeContainer]:
        self.list_calls.append(kwargs)
        return self.listed


class FakeClient:
    def __init__(
        self,
        images: FakeImages | None = None,
        volumes: FakeVolumes | None = None,
        containers: FakeContainers | None = None,
        info_data: dict[str, Any] | None = None,
    ) -> None:
        self.images = images or FakeImages()
        self.volumes = volumes or FakeVolumes()
        self.containers = containers or FakeContainers()
        self.info_data = info_data or {"OSType": "linux"}
        self.ping_calls = 0

    def ping(self) -> bool:
        self.ping_calls += 1
        return True

    def info(self) -> dict[str, Any]:
        return self.info_data
