"""Compression command definitions for backup archives."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath
import shlex


DEFAULT_COMPRESSION = "gzip"
SUPPORTED_COMPRESSIONS = (
    "gzip",
    "xz",
    "zstd",
    "bzip2",
    "bzip3",
    "7z",
    "zip",
)


@dataclass(frozen=True)
class Compression:
    """Compression metadata for one backup archive format.

    Parameters
    ----------
    name : str
        Command-line compression choice.
    suffix : str
        File suffix appended to backup archive names.
    compress_command : str
        Shell pipeline fragment that compresses a tar stream from
        standard input and writes the completed archive to ``{target}``.
    extract_command : str
        Shell pipeline fragment that reads ``{source}`` and writes a tar
        stream to standard output.
    restore_template : str or None
        Full restore shell command template for formats that cannot
        safely stream extraction through standard output.
    """

    name: str
    suffix: str
    compress_command: str
    extract_command: str
    restore_template: str | None = None

    def backup_command(self, target: PurePosixPath) -> str:
        """Return the shell command that creates a compressed backup.

        Parameters
        ----------
        target : PurePosixPath
            Backup archive path inside the helper container.

        Returns
        -------
        str
            Shell command suitable for ``sh -c``.
        """
        quoted_target = shlex.quote(str(target))
        return (
            "set -e; "
            f"tar -cf - /recover | {self.compress_command.format(target=quoted_target)}"
        )

    def restore_command(self, source: PurePosixPath) -> str:
        """Return the shell command that restores a compressed backup.

        Parameters
        ----------
        source : PurePosixPath
            Backup archive path inside the helper container.

        Returns
        -------
        str
            Shell command suitable for ``sh -c``.
        """
        quoted_source = shlex.quote(str(source))
        if self.restore_template:
            return self.restore_template.format(source=quoted_source)
        extractor = self.extract_command.format(source=quoted_source)
        return f"set -e; cd /recover && {extractor} | tar -xf - --strip 1"


COMPRESSIONS = {
    "gzip": Compression("gzip", ".tar.gz", "gzip -c > {target}", "gzip -cd {source}"),
    "xz": Compression("xz", ".tar.xz", "xz -c > {target}", "xz -cd {source}"),
    "zstd": Compression("zstd", ".tar.zst", "zstd -c > {target}", "zstd -cd {source}"),
    "bzip2": Compression(
        "bzip2",
        ".tar.bz2",
        "bzip2 -c > {target}",
        "bzip2 -cd {source}",
    ),
    "bzip3": Compression(
        "bzip3",
        ".tar.bz3",
        "bzip3 -c > {target}",
        "bzip3 -cd {source}",
    ),
    "7z": Compression(
        "7z",
        ".tar.7z",
        "7zz a {target} -si'recover.tar' >/dev/null",
        "",
        (
            "set -e; rm -rf /tmp/vbart-restore && mkdir /tmp/vbart-restore "
            "&& 7zz x -o/tmp/vbart-restore {source} >/dev/null "
            "&& cd /recover "
            "&& tar -xf /tmp/vbart-restore/recover.tar --strip 1"
        ),
    ),
    "zip": Compression(
        "zip",
        ".tar.zip",
        "zip -q {target} -",
        "unzip -p {source}",
    ),
}


def get_compression(name: str) -> Compression:
    """Return compression metadata for a command-line choice.

    Parameters
    ----------
    name : str
        Compression choice.

    Returns
    -------
    Compression
        Compression metadata.
    """
    return COMPRESSIONS[name]


def compression_from_path(path: Path) -> Compression | None:
    """Return compression metadata inferred from an archive path.

    Parameters
    ----------
    path : Path
        Backup archive path.

    Returns
    -------
    Compression or None
        Matching compression metadata, or ``None`` when unsupported.
    """
    name = path.name
    for compression in COMPRESSIONS.values():
        if name.endswith(compression.suffix):
            return compression
    return None
