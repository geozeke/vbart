from __future__ import annotations

import pytest

from vbart.classes import ExhaustedListError
from vbart.classes import Labels


def test_labels_next_prints_first_label(
    capsys: pytest.CaptureFixture[str],
) -> None:
    labels = Labels("first\nsecond")

    labels.next()

    out = capsys.readouterr().out
    assert out.startswith("first")
    assert set(out[len("first") :]) == {"."}
    assert labels.labels == ["second"]


def test_labels_raises_on_empty_list() -> None:
    labels = Labels("only")
    labels.pop_first()

    with pytest.raises(ExhaustedListError):
        labels.pop_last()


def test_pop_item_exits_on_invalid_index(
    capsys: pytest.CaptureFixture[str],
) -> None:
    labels = Labels("one")

    with pytest.raises(SystemExit) as exc:
        labels.pop_item(5)

    assert exc.value.code == 1
    assert "Attempting to pop index 5." in capsys.readouterr().out
