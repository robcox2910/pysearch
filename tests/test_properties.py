"""Property-based tests -- rules that must hold for *every* input.

An ordinary test checks one example someone thought of: "file a book that
says ``cat dog``, search for ``cat``, and that book comes back". A property
test states a rule instead, such as "the engine finds exactly the books a
librarian reading every book would find", and lets Hypothesis invent
hundreds of libraries and questions to try to break it. If one breaks the
rule, Hypothesis *shrinks* it down to the smallest input that still fails,
and shows you that.

Each test below says its rule in plain English in its docstring. The
strategies are recipes for making random inputs; each one is named for
what it makes.

The step-by-step check of ``SearchEngine`` against the brute-force
librarian lives in ``tests/test_model.py``. See ``docs/property-testing.md``
for the walk-through.
"""

import json
import tempfile
from itertools import pairwise
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from pysearch.engine import SearchEngine
from pysearch.errors import PersistenceError, QueryParseError
from pysearch.persistence import load_engine, save_engine
from pysearch.tokenizer import split_words
from tests.brute_force import Book, brute_force_search, text_of
from tests.strategies import doc_ids, libraries, questions

# --- Strategies: recipes for random inputs -----------------------------------
# doc_ids(), libraries() and questions() live in tests/strategies.py, shared
# with the model check.

# A JSON document is built from at most this many plain pieces. Small ones
# find the same bugs, and a failure shrinks to a small one anyway.
MOST_PIECES_PER_DOCUMENT = 10


def any_texts() -> st.SearchStrategy[dict[str, str]]:
    """Make any books at all: any ids, each with any text, emoji and all."""
    return st.dictionaries(doc_ids(), st.text())


def any_bytes() -> st.SearchStrategy[bytes]:
    """Make any run of raw bytes, including the empty one and ones that aren't text."""
    return st.binary()


def any_json() -> st.SearchStrategy[object]:
    """Make any JSON document at all: numbers, text, lists and objects inside each other."""
    return st.recursive(
        st.one_of(st.none(), st.booleans(), st.integers(), st.floats(), st.text()),
        lists_and_objects_of,
        max_leaves=MOST_PIECES_PER_DOCUMENT,
    )


def lists_and_objects_of(children: st.SearchStrategy[object]) -> st.SearchStrategy[object]:
    """Make a JSON list, or a JSON object with text keys, holding ``children``."""
    return st.one_of(st.lists(children), st.dictionaries(st.text(), children))


def save_shaped_json() -> st.SearchStrategy[object]:
    """Make JSON that looks like a saved engine: format 1 (or anything), any documents."""
    return st.fixed_dictionaries(
        {
            "format": st.one_of(st.just(1), any_json()),
            "documents": st.one_of(st.dictionaries(st.text(), any_json()), any_json()),
        }
    )


# --- Helpers -----------------------------------------------------------------


def engine_holding(library: dict[str, Book]) -> SearchEngine:
    """Return a new engine with every book in ``library`` added under its id."""
    engine = SearchEngine()
    for doc_id, book in library.items():
        engine.add(doc_id, text_of(book))
    return engine


def load_or_refuse(path: Path) -> None:
    """Load the engine at ``path``, accepting only a PersistenceError refusal.

    A PersistenceError is caught and ignored: refusing a bad file is fine. Any
    *other* exception escapes and fails the test, and that is the whole check.
    """
    try:
        load_engine(path)
    except PersistenceError:
        return


# --- Searching: the right books, in the right order --------------------------


@given(library=libraries(), question=questions())
def test_search_finds_what_reading_every_book_finds(
    library: dict[str, Book], question: list[str]
) -> None:
    """The engine gives exactly the brute-force librarian's books, scores and order."""
    engine = engine_holding(library)
    answer = engine.search(" ".join(question))
    assert answer == brute_force_search(library, question)


@given(library=libraries(), question=questions())
def test_results_come_best_first_and_ties_by_id(
    library: dict[str, Book], question: list[str]
) -> None:
    """Scores never go up as you read down the results, and equal scores are in id order."""
    answer = engine_holding(library).search(" ".join(question))
    for (first_id, first_score), (next_id, next_score) in pairwise(answer):
        assert first_score >= next_score
        if first_score == next_score:
            assert first_id < next_id


@given(texts=any_texts(), question=st.text())
def test_any_question_gives_results_or_query_parse_error(
    texts: dict[str, str], question: str
) -> None:
    """Whatever you type, search gives a list of books in the library or a QueryParseError."""
    engine = SearchEngine()
    for doc_id, text in texts.items():
        engine.add(doc_id, text)
    try:
        answer = engine.search(question)
    except QueryParseError:
        return
    assert {doc_id for doc_id, _score in answer} <= set(texts)


# --- Save and load: whatever you save comes back ------------------------------


@given(texts=any_texts())
def test_save_then_load_gives_back_the_same_engine(texts: dict[str, str]) -> None:
    """A loaded engine holds the same books and answers every question the same way."""
    original = SearchEngine()
    for doc_id, text in texts.items():
        original.add(doc_id, text)
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "engine.json"
        save_engine(original, path)
        loaded = load_engine(path)
    # ``repr`` also checks the order the books were filed in, and every type.
    assert repr(loaded.to_dict()) == repr(original.to_dict())
    # Ask about every word really in the books (random text seldom holds
    # "cat" or "dog", so a fixed word list would mostly compare [] with []).
    for word in sorted({word for text in texts.values() for word in split_words(text)}):
        assert loaded.search(word) == original.search(word)


# --- Loading junk: a bad save file is refused, never a crash ------------------


@given(junk=any_bytes())
def test_any_bytes_on_disk_load_or_raise_persistence_error(junk: bytes) -> None:
    """Whatever bytes are in the file, loading gives an engine or a PersistenceError."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "engine.json"
        path.write_bytes(junk)
        load_or_refuse(path)


@given(document=save_shaped_json())
def test_any_save_shaped_json_load_or_raise_persistence_error(document: object) -> None:
    """Whatever a save-shaped JSON file holds, loading gives an engine or a PersistenceError."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "engine.json"
        path.write_text(json.dumps(document), encoding="utf-8")
        load_or_refuse(path)


@given(version=any_json().filter(lambda value: type(value) is not int or value != 1))
def test_any_format_but_the_int_one_is_refused(version: object) -> None:
    """A save file whose format is not exactly the int 1 (``true``, ``1.0``, ...) is refused."""
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "engine.json"
        path.write_text(json.dumps({"format": version, "documents": {}}), encoding="utf-8")
        with pytest.raises(PersistenceError, match=r"engine\.json"):
            load_engine(path)
