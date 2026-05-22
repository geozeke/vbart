from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "dependency_upgrade_commit.py"
)
SPEC = importlib.util.spec_from_file_location("dependency_upgrade_commit", SCRIPT_PATH)
assert SPEC is not None
dependency_upgrade_commit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = dependency_upgrade_commit
SPEC.loader.exec_module(dependency_upgrade_commit)


def test_first_order_dependencies_include_runtime_and_groups(
    tmp_path: Path,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = [
    "Docker>=7.1.0",
    "rich[markdown]>=14.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=7.0.0",
]
types = ["mypy>=1.13.0"]
""",
        encoding="utf-8",
    )

    dependencies = dependency_upgrade_commit.first_order_dependencies(pyproject)

    assert dependencies == {
        "docker": "Docker",
        "mypy": "mypy",
        "pytest": "pytest",
        "pytest-cov": "pytest-cov",
        "rich": "rich",
    }


def test_locked_versions_ignore_editable_local_package(tmp_path: Path) -> None:
    lockfile = tmp_path / "uv.lock"
    lockfile.write_text(
        """
[[package]]
name = "vbart"
version = "0.3.3"
source = { editable = "." }

[[package]]
name = "pytest-cov"
version = "7.0.0"
source = { registry = "https://pypi.org/simple" }
""",
        encoding="utf-8",
    )

    assert dependency_upgrade_commit.locked_versions(lockfile) == {
        "pytest-cov": "7.0.0",
    }


def test_dependency_updates_ignore_transitive_only_changes() -> None:
    dependencies = {"docker": "docker", "pytest": "pytest"}
    before_versions = {
        "docker": "7.1.0",
        "pytest": "8.4.2",
        "requests": "2.32.4",
    }
    after_versions = {
        "docker": "7.1.0",
        "pytest": "9.0.3",
        "requests": "2.32.5",
    }

    updates = dependency_upgrade_commit.dependency_updates(
        dependencies,
        before_versions,
        after_versions,
    )

    assert updates == [
        dependency_upgrade_commit.DependencyUpdate(
            name="pytest",
            old_version="8.4.2",
            new_version="9.0.3",
        ),
    ]


def test_outdated_first_order_packages_ignore_transitive_packages() -> None:
    dependencies = {
        "docker": "Docker",
        "pytest": "pytest",
        "pytest-cov": "pytest-cov",
    }
    tree_output = """
vbart v0.3.3
├── Docker v7.1.0 (latest: v7.2.0)
│   └── urllib3 v2.4.0 (latest: v2.6.0)
├── pytest v8.4.2 (latest: v9.0.3)
├── pytest-cov v7.0.0 (latest: v7.1.0)
└── requests v2.32.4 (latest: v2.32.5)
"""

    packages = dependency_upgrade_commit.outdated_first_order_packages(
        dependencies,
        tree_output,
    )

    assert packages == ["Docker", "pytest", "pytest-cov"]


def test_outdated_command_prints_first_order_packages(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """
[project]
dependencies = ["docker>=7.1.0"]

[dependency-groups]
dev = ["pytest>=8.4.2"]
""",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        sys,
        "stdin",
        io.StringIO(
            "├── docker v7.1.0 (latest: v7.2.0)\n└── urllib3 v2.4.0 (latest: v2.6.0)\n"
        ),
    )

    result = dependency_upgrade_commit.main(
        [
            "outdated",
            "--pyproject",
            str(pyproject),
        ]
    )

    assert result == 0
    assert capsys.readouterr().out == "docker\n"


def test_render_commit_message_uses_exact_subject_and_body() -> None:
    message = dependency_upgrade_commit.render_commit_message(
        [
            dependency_upgrade_commit.DependencyUpdate(
                name="rich",
                old_version="14.0.0",
                new_version="15.0.0",
            ),
            dependency_upgrade_commit.DependencyUpdate(
                name="pytest",
                old_version="8.3.5",
                new_version="9.0.3",
            ),
        ]
    )

    assert message == (
        "deps: DEPS-See commit msg for list\n"
        "\n"
        "- rich: 14.0.0 -> 15.0.0\n"
        "- pytest: 8.3.5 -> 9.0.3\n"
    )


def test_message_command_returns_nonzero_without_direct_updates(
    tmp_path: Path,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    lockfile = tmp_path / "uv.lock"
    before = tmp_path / "before.json"
    output = tmp_path / "message.txt"
    pyproject.write_text(
        """
[project]
dependencies = ["docker>=7.1.0"]

[dependency-groups]
dev = ["pytest>=8.4.2"]
""",
        encoding="utf-8",
    )
    lockfile.write_text(
        """
[[package]]
name = "docker"
version = "7.1.0"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "pytest"
version = "8.4.2"
source = { registry = "https://pypi.org/simple" }

[[package]]
name = "requests"
version = "2.32.5"
source = { registry = "https://pypi.org/simple" }
""",
        encoding="utf-8",
    )
    before.write_text(
        json.dumps(
            {
                "docker": "7.1.0",
                "pytest": "8.4.2",
                "requests": "2.32.4",
            }
        ),
        encoding="utf-8",
    )

    result = dependency_upgrade_commit.main(
        [
            "message",
            "--pyproject",
            str(pyproject),
            "--lockfile",
            str(lockfile),
            "--before",
            str(before),
            "--output",
            str(output),
        ]
    )

    assert result == 1
    assert not output.exists()
