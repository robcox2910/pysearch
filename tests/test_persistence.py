"""Test saving a search engine to disk and loading it back.

A saved engine is like a librarian's notebook: close the library for the
night, and tomorrow she can open the notebook and find every book again.
"""

import json
import os
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pysearch.engine import SearchEngine
from pysearch.errors import PersistenceError, PySearchError
from pysearch.persistence import load_engine, save_engine

WORDS = st.text(alphabet="abcdefghij", min_size=1, max_size=6)
DOCUMENTS = st.lists(
    st.tuples(
        st.text(alphabet="xyz0123456789", min_size=1, max_size=8), st.lists(WORDS, max_size=8)
    ),
    max_size=8,
    unique_by=lambda doc: doc[0],
)
MAX_EXAMPLES = 50


def _answer(engine: SearchEngine, query: str) -> object:
    """Return the engine's results for *query*, or the kind of error it raised."""
    try:
        return engine.search(query)
    except PySearchError as exc:
        return type(exc)


class TestRoundTrip:
    """An engine saved and loaded answers every question the same way."""

    @settings(max_examples=MAX_EXAMPLES)
    @given(DOCUMENTS)
    def test_round_trip_gives_identical_search_results(
        self, tmp_path_factory: pytest.TempPathFactory, documents: list[tuple[str, list[str]]]
    ) -> None:
        """For every word in the documents, both engines give the same results."""
        original = SearchEngine()
        for doc_id, words in documents:
            original.add(doc_id, " ".join(words))
        path = tmp_path_factory.mktemp("save") / "engine.json"

        save_engine(original, path)
        loaded = load_engine(path)

        assert loaded.document_count == original.document_count
        for word in {w for _, words in documents for w in words}:
            assert _answer(loaded, word) == _answer(original, word)

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
