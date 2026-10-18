"""Model check -- SearchEngine must answer exactly like a librarian who reads every book.

A property test checks one rule for many inputs. A *model check* goes
further: Hypothesis invents a random *story* -- add this book, try to add
that one again, ask a question, save and reload -- and plays it on two
things at once:

- the real ``SearchEngine``, with its inverted index;
- a **model**: a plain ``dict`` of doc id -> words, searched by the
  brute-force librarian in ``tests/brute_force.py``, who rereads every
  book for every question.

After every step the two must agree. If they ever disagree, Hypothesis
shrinks the story to the shortest list of steps that still goes wrong.

The model is deliberately *not* a copy of ``SearchEngine``'s code. It keeps
no index at all, so when the two disagree, the engine is the one to suspect.

See ``docs/property-testing.md`` for the walk-through.
"""

import unittest
from typing import cast

import pytest
from hypothesis import settings
from hypothesis.stateful import Bundle, RuleBasedStateMachine, invariant, rule

from pysearch.engine import SearchEngine
from pysearch.errors import DuplicateDocumentError
from tests.brute_force import Book, brute_force_search, text_of
from tests.strategies import books, doc_ids, questions

# --- The machine: one story, played on the engine and on a dict ---------------


class SearchEngineMachine(RuleBasedStateMachine):
    """Play random adds, questions and reloads on a SearchEngine and a dict side by side."""

    # Ids we've used before. Brand-new random ids almost never repeat, so
    # rules also pick from here to try adding a book under a taken id.
    ids = Bundle("ids")

    def __init__(self) -> None:
        """Start with an empty engine and an empty dict."""
        super().__init__()
        self.engine = SearchEngine()
        self.model: dict[str, Book] = {}

    @rule(target=ids, doc_id=doc_ids(), book=books())
    def add_book(self, doc_id: str, book: Book) -> str:
        """Add a book under any id: a new id is filed, a taken one is refused."""
        if doc_id in self.model:
            with pytest.raises(DuplicateDocumentError):
                self.engine.add(doc_id, text_of(book))
        else:
            self.engine.add(doc_id, text_of(book))
            self.model[doc_id] = book
        return doc_id

    @rule(doc_id=ids, book=books())
    def add_book_under_a_taken_id(self, doc_id: str, book: Book) -> None:
        """Adding a book under an id already in the engine is refused, and changes nothing."""
        with pytest.raises(DuplicateDocumentError):
            self.engine.add(doc_id, text_of(book))

    @rule(question=questions())
    def ask(self, question: list[str]) -> None:
        """Ask a question: the engine gives the brute-force librarian's answer."""
        expected = brute_force_search(self.model, question)
        assert self.engine.search(" ".join(question)) == expected

    @rule()
    def save_and_reload(self) -> None:
        """Rebuild the engine from its saved data; nothing it knows may change."""
        saved = self.engine.to_dict()
        self.engine = SearchEngine.from_dict(saved)
        # The new engine must have its own copy, not lean on the dict it was given.
        cast("dict[str, str]", saved["documents"]).clear()

    @rule()
    def scribble_on_saved_data(self) -> None:
        """Mess up the dict to_dict handed out; the engine must keep its own copy."""
        saved = self.engine.to_dict()
        saved["format"] = "scribbled"
        documents = cast("dict[str, str]", saved["documents"])
        documents.clear()
        documents["scribble"] = "cats"

    @invariant()
    def same_books(self) -> None:
        """After every step, the engine holds exactly the dict's books, in filing order."""
        texts = {doc_id: text_of(book) for doc_id, book in self.model.items()}
        assert self.engine.document_count == len(self.model)
        # repr also checks the order: books are saved in the order they were filed.
        assert repr(self.engine.to_dict()) == repr({"format": 1, "documents": texts})


# why: 20 steps find the same bugs; 50 (the default) is most of the run time
SearchEngineMachine.TestCase.settings = settings(stateful_step_count=20)
# pytest runs this like any other test class: one run plays 100 random stories.
# (Hypothesis doesn't say what type ``TestCase`` is, so ``cast`` tells pyright.)
TestSearchEngineModel = cast("type[unittest.TestCase]", SearchEngineMachine.TestCase)
