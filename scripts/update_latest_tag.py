"""Move the mutable ``latest`` tag after a successful stable release."""

from __future__ import annotations

import argparse
import subprocess


def main() -> None:
    """Force-update ``latest`` only when it matches the newest release.

    Raises
    ------
    SystemExit
        If the release is not the newest stable GitHub release.
    subprocess.CalledProcessError
        If Git cannot update the mutable tag.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_tag")
    parser.add_argument("latest_release_tag")
    parser.add_argument("commit")
    args = parser.parse_args()
    if args.release_tag != args.latest_release_tag:
        raise SystemExit(
            "Refusing to move latest: release is not the newest stable tag"
        )
    subprocess.run(("git", "tag", "-f", "latest", args.commit), check=True)
    subprocess.run(("git", "push", "--force", "origin", "refs/tags/latest"), check=True)


if __name__ == "__main__":
    main()
