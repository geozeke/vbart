"""Runtime compatibility helpers for Docker-backed execution."""

from typing import Any
from typing import Protocol
from pathlib import Path
import sys

import docker  # type:ignore


class UnsupportedRuntimeError(RuntimeError):
    """Raised when the current host/runtime combination is unsupported."""


class SupportsDockerInfo(Protocol):
    """Minimal Docker client surface needed for runtime-mode checks."""

    def info(self) -> dict[str, Any]:
        """Return Docker daemon information."""
        ...


def is_windows_host() -> bool:
    """Return whether vbart is running on a Windows host."""
    return sys.platform == "win32"


def normalize_bind_source(path: Path) -> str:
    """Normalize a host path for Docker bind mounts."""
    source = str(path.resolve())
    if is_windows_host():
        return source.replace("\\", "/")
    return source


def validate_runtime_mode(client: SupportsDockerInfo) -> None:
    """Validate platform-specific Docker runtime constraints."""
    if not is_windows_host():
        return

    os_type = str(client.info().get("OSType", "")).lower()
    if os_type != "linux":
        msg = (
            "vbart supports Windows only when Docker is running Linux "
            "containers. Switch Docker Desktop to Linux containers and "
            "try again."
        )
        raise UnsupportedRuntimeError(msg)


def get_docker_client() -> docker.DockerClient:  # type: ignore
    """Return a Docker client after validating runtime availability."""
    # Preserve pre-7.2.0 Docker SDK behavior: vbart honors Docker
    # environment variables, but does not follow Docker CLI contexts.
    from_env_kwargs: dict[str, Any] = {"use_context": False}
    client = docker.from_env(**from_env_kwargs)
    client.ping()
    validate_runtime_mode(client)
    return client
