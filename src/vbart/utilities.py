"""Utilities for backing up and restoring Docker volumes."""

import tempfile as tf
from datetime import datetime as dt
from pathlib import Path
from pathlib import PurePosixPath
import shlex
from typing import Any

from docker import errors  # type:ignore

from vbart.compression import DEFAULT_COMPRESSION
from vbart.compression import get_compression
from vbart.constants import BASE_IMAGE
from vbart.constants import FAIL
from vbart.constants import HELPER_IMAGE_VERSION
from vbart.constants import HELPER_IMAGE_VERSION_LABEL
from vbart.constants import PASS
from vbart.constants import UTILITY_IMAGE
from vbart.runtime import get_docker_client
from vbart.runtime import normalize_bind_source

# ======================================================================


def verify_utility_image() -> None:
    """Ensure that the helper image is available.

    If the helper image is missing, build it and remove any temporary
    image dependencies created during the build.
    """
    # NOTE: The python docker package is not typed, so you'll see lots
    # of "type: ignore" hashtags sprinkled throughout.

    client = get_docker_client()
    try:
        image = client.images.get(UTILITY_IMAGE)
        if helper_image_is_current(image):
            return
    except errors.ImageNotFound:
        pass

    # If the alpine image is already installed, don't delete it after
    # creating the utility image.

    try:
        client.images.get(BASE_IMAGE)
        alpine_already_present = True
    except errors.ImageNotFound:
        alpine_already_present = False

    msg = "Building utility image (this is a one-time operation)..."
    print(f"{msg}", end="", flush=True)
    with tf.TemporaryDirectory() as build_dir:
        dockerfile_path = Path(build_dir) / "Dockerfile"
        dockerfile_path.write_text(render_helper_dockerfile(), encoding="utf-8")
        client.images.build(
            path=build_dir,
            tag=f"{UTILITY_IMAGE}:latest",
            nocache=True,
            rm=True,
        )

    # Saving and reloading the image flattens it so it will operate
    # standalone, meaning it won't need any parent image dependencies.

    utility_image = client.images.get(UTILITY_IMAGE)
    with tf.TemporaryFile(mode="w+b") as f:
        for chunk in utility_image.save(named=True):  # type: ignore
            f.write(chunk)
        f.seek(0)
        client.images.remove(UTILITY_IMAGE)
        if not alpine_already_present:
            client.images.remove(BASE_IMAGE)
        client.images.load(f.read())
    print("Done")
    return


# ======================================================================


def render_helper_dockerfile() -> str:
    """Render the helper-image Dockerfile from runtime constants."""
    return (
        f"FROM {BASE_IMAGE}\n"
        f'LABEL {HELPER_IMAGE_VERSION_LABEL}="{HELPER_IMAGE_VERSION}"\n'
        "RUN apk -U upgrade\n"
        "# Add support for selectable backup compression.\n"
        "RUN apk add --no-cache 7zip bzip2 bzip3 gzip tar unzip xz zip zstd\n"
    )


# ======================================================================


def helper_image_is_current(image: Any) -> bool:
    """Return whether an existing helper image matches this version.

    Parameters
    ----------
    image : Any
        Docker image object returned by the Docker SDK.

    Returns
    -------
    bool
        ``True`` when the image has the expected helper-version label.
    """
    labels = getattr(image, "attrs", {}).get("Config", {}).get("Labels") or {}
    return labels.get(HELPER_IMAGE_VERSION_LABEL) == HELPER_IMAGE_VERSION


# ======================================================================


def backup_one_volume(
    volume: str,
    compression_name: str = DEFAULT_COMPRESSION,
) -> str:
    """Back up a single named volume.

    Parameters
    ----------
    volume : str
        Name of the volume to back up.
    compression_name : str
        Compression algorithm to use.

    Returns
    -------
    str
        ``PASS`` if the backup succeeds, otherwise ``FAIL``.
    """
    client = get_docker_client()
    now = dt.now()
    prefix = f"{now.year}{now.month:02d}{now.day:02d}"
    compression = get_compression(compression_name)
    p = Path(f"{prefix}-{volume}-backup{compression.suffix}")
    volume_map = {
        volume: {"bind": "/recover", "mode": "rw"},
        normalize_bind_source(p.parent): {"bind": "/backup", "mode": "rw"},
    }
    backup_path = PurePosixPath("/backup") / p.name
    shell_arg = shlex.quote(compression.backup_command(backup_path))
    shell_cmd = f"sh -c {shell_arg}"

    # Run the container and perform the backup.

    try:
        client.containers.run(
            image=UTILITY_IMAGE,
            command=shell_cmd,
            remove=True,
            volumes=volume_map,  # type:ignore
        )
        return PASS
    except errors.ContainerError:
        return FAIL
