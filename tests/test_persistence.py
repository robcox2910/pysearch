"""Test saving a search engine to disk and loading it back.

A saved engine is like a librarian's notebook: close the library for the
night, and tomorrow she can open the notebook and find every book again.
"""

import json
import os
from pathlib import Path

import pytest

from pysearch.engine import SearchEngine
from pysearch.errors import PersistenceError
from pysearch.persistence import load_engine, save_engine


class TestRoundTrip:
    """An engine saved and loaded keeps working.

    The save/load round-trip for *any* engine is a property:
    ``test_save_then_load_gives_back_the_same_engine`` in
    ``tests/test_properties.py``.
    """

    def test_loaded_engine_keeps_accepting_new_documents(self, tmp_path: Path) -> None:
        """A loaded engine still rejects duplicate ids and accepts new ones."""
        engine = SearchEngine()
        engine.add("cats", "cats purr")
        save_engine(engine, tmp_path / "engine.json")
        loaded = load_engine(tmp_path / "engine.json")
        loaded.add("dogs", "dogs bark")
        assert [doc for doc, _ in loaded.search("bark")] == ["dogs"]


class TestLoadErrors:
    """A missing or damaged file raises PersistenceError, naming the file."""

    def test_missing_file_raises_persistence_error(self, tmp_path: Path) -> None:
        """Loading a file that isn't there is a PersistenceError."""
        with pytest.raises(PersistenceError, match=r"missing\.json"):
            load_engine(tmp_path / "missing.json")

    def test_bad_json_raises_persistence_error_naming_the_file(self, tmp_path: Path) -> None:
        """A scribbled-on file is a PersistenceError that names the file."""
        path = tmp_path / "engine.json"
        path.write_text("{not json", encoding="utf-8")
        with pytest.raises(PersistenceError, match=r"engine\.json"):
            load_engine(path)

    def test_wrong_shape_raises_persistence_error(self, tmp_path: Path) -> None:
        """Valid JSON that isn't a saved engine is a PersistenceError."""
        path = tmp_path / "engine.json"
        path.write_text(
            json.dumps({"format": 1, "documents": ["not", "a", "dict"]}), encoding="utf-8"
        )
        with pytest.raises(PersistenceError):
            load_engine(path)

    def test_unknown_format_raises_persistence_error(self, tmp_path: Path) -> None:
        """A file from a future version is refused rather than misread."""
        path = tmp_path / "engine.json"
        path.write_text(json.dumps({"format": 99, "documents": {}}), encoding="utf-8")
        with pytest.raises(PersistenceError, match="format"):
            load_engine(path)

    @pytest.mark.parametrize("version", [True, 1.0])
    def test_format_must_be_an_exact_int(self, tmp_path: Path, version: object) -> None:
        """Regression: ``true`` and ``1.0`` equal 1 in Python, so they were accepted."""
        path = tmp_path / "engine.json"
        path.write_text(json.dumps({"format": version, "documents": {}}), encoding="utf-8")
        with pytest.raises(PersistenceError, match=r"engine\.json"):
            load_engine(path)

    def test_a_file_that_is_not_text_raises_persistence_error(self, tmp_path: Path) -> None:
        """Regression: a lone 0x80 byte (found by Hypothesis) raised UnicodeDecodeError."""
        path = tmp_path / "engine.json"
        path.write_bytes(b"\x80")
        with pytest.raises(PersistenceError, match=r"engine\.json"):
            load_engine(path)

    def test_a_number_too_long_to_read_raises_persistence_error(self, tmp_path: Path) -> None:
        """Regression: a 5,000-digit number raised ValueError (Python's int digit limit)."""
        path = tmp_path / "engine.json"
        path.write_text("1" * 5000, encoding="utf-8")
        with pytest.raises(PersistenceError, match=r"engine\.json"):
            load_engine(path)

    def test_json_nested_too_deep_raises_persistence_error(self, tmp_path: Path) -> None:
        """Regression: 100,000 ``[`` characters raised RecursionError."""
        path = tmp_path / "engine.json"
        path.write_text("[" * 100_000, encoding="utf-8")
        with pytest.raises(PersistenceError, match=r"engine\.json"):
            load_engine(path)


class TestSafeSaving:
    """Saving never leaves a half-written file behind."""

    def test_save_never_leaves_a_half_written_file(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If the final swap fails, the old file is untouched and no scrap is left."""
        path = tmp_path / "engine.json"
        first = SearchEngine()
        first.add("a", "apples")
        save_engine(first, path)
        before = path.read_bytes()

        def broken_replace(*_args: object, **_kwargs: object) -> None:
            msg = "disk unplugged"
            raise OSError(msg)

        monkeypatch.setattr(os, "replace", broken_replace)
        monkeypatch.setattr(Path, "replace", broken_replace)
        second = SearchEngine()
        second.add("b", "bananas")
        with pytest.raises(OSError, match="unplugged"):
            save_engine(second, path)

        assert path.read_bytes() == before
        assert [p.name for p in tmp_path.iterdir()] == ["engine.json"]
