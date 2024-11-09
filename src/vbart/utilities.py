"""Utilities to support docker volume backup/restore."""

import tempfile as tf
from datetime import datetime as dt
from pathlib import Path

import docker  # type:ignore
from docker import errors

from vbart.constants import BASE_IMAGE
from vbart.constants import DOCKERFILE_PATH
from vbart.constants import FAIL
from vbart.constants import PASS
from vbart.constants import UTILITY_IMAGE

# ======================================================================


def verify_utility_image() -> None:
    """Verify the backup utility image is in place.

    If the utility image is not present, then build it. Also delete any
    interim build products (images) that were created.
    """
    # NOTE: The python docker package is not typed, so you'll see lots
    # of "type: ignore" hashtags sprinkled throughout.

    client = docker.from_env()
    try:
        client.images.get(UTILITY_IMAGE)
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
    client.images.build(
        path=str(DOCKERFILE_PATH),
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


def backup_one_volume(volume: str) -> str:
    """Perform a backup on a single named volume.

    Parameters
    ----------
    volume : str
        The name of the volume to backup

    Returns
    -------
    str
        Return either PASS or FAIL, depending on the result of the
        backup.
    """
    client = docker.from_env()
    now = dt.now()
    prefix = f"{now.year}{now.month:02d}{now.day:02d}"
    p = Path(f"{prefix}-{volume}-backup.xz")
    volume_map = {
        volume: {"bind": "/recover", "mode": "rw"},
        p.parent.absolute(): {"bind": "/backup", "mode": "rw"},
    }
    cmd = f"tar cavf /backup/{p.name} /recover"

    # Run the container and perform the backup.

    try:
        client.containers.run(
            image=UTILITY_IMAGE,
            command=cmd,
            remove=True,
            volumes=volume_map,  # type:ignore
        )
        return PASS
    except errors.ContainerError:
        return FAIL
