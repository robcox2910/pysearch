"""Tie every component together into a complete search engine.

The search engine is the librarian herself. She knows how to file new books
(add documents), understand your question (parse queries), look things up
(search the index), and tell you which results matter most (rank by TF-IDF).
"""

from typing import Self, cast

from pysearch.index import InvertedIndex
from pysearch.query import AndQuery, SearchQuery, TermQuery, parse_query
from pysearch.tfidf import rank_results

# Bump this if the saved layout ever changes, so old files are refused, not misread.
SAVE_FORMAT = 1


class SearchEngine:
    """A full-text search engine with TF-IDF ranking and boolean queries."""

    def __init__(self) -> None:
        """Initialise an empty search engine."""
        self._index = InvertedIndex()
        # The original text of every book, in the order it arrived, so the
        # engine can be saved and rebuilt exactly.
        self._documents: dict[str, str] = {}

    def add(self, doc_id: str, text: str) -> None:
        """Hand the librarian a new book to file away.

        Args:
            doc_id: A unique identifier for the document.
            text: The raw document text.

        """
        self._index.add_document(doc_id, text)
        self._documents[doc_id] = text

    def to_dict(self) -> dict[str, object]:
        """Return everything needed to rebuild this engine, as plain data.

        Returns:
            ``{"format": 1, "documents": {doc_id: text, ...}}``

        """
        return {"format": SAVE_FORMAT, "documents": dict(self._documents)}

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Self:
        """Rebuild an engine from :meth:`to_dict` data by re-filing every book.

        Args:
            data: The saved data.

        Returns:
            A new engine holding the same documents.

        Raises:
            ValueError: If *data* is from an unknown format version.
            TypeError: If *data* doesn't have the expected shape.

        """
        if data.get("format") != SAVE_FORMAT:
            msg = f"unknown save format {data.get('format')!r} (expected {SAVE_FORMAT})"
            raise ValueError(msg)
        documents = data["documents"]
        if not isinstance(documents, dict):
            msg = "'documents' must be an object mapping ids to text"
            raise TypeError(msg)
        engine = cls()
        for doc_id, text in cast("dict[object, object]", documents).items():
            if not isinstance(doc_id, str) or not isinstance(text, str):
                msg = "every document id and text must be a string"
                raise TypeError(msg)
            engine.add(doc_id, text)
        return engine

    def search(self, query_text: str) -> list[tuple[str, float]]:
        """Ask the librarian a question and get back the best-matching books, best first.

        Args:
            query_text: A query string such as ``"cats"``, ``"cats AND dogs"``,
                or ``"cats OR dogs"``.

        Returns:
            A list of ``(doc_id, score)`` tuples sorted by relevance.

        """
        query = parse_query(query_text)
        doc_ids = self._execute(query)

        if not doc_ids:
            return []

        # Rank by ALL terms in the query so every word counts.
        all_terms = self._collect_terms(query)
        return rank_results(all_terms, doc_ids, self._index)

    @property
    def document_count(self) -> int:
        """Return the total number of indexed documents."""
        return self._index.document_count

    def _execute(self, query: SearchQuery) -> list[str]:
        """Recursively execute a parsed query against the index.

        Args:
            query: A parsed ``SearchQuery`` tree.

        Returns:
            A list of matching document IDs.

        """
        if isinstance(query, TermQuery):
            return self._index.search(query.term)
        if isinstance(query, AndQuery):
            left = set(self._execute(query.left))
            right = set(self._execute(query.right))
            return list(left & right)
        # Must be OrQuery (type narrowing guarantees this).
        left = set(self._execute(query.left))
        right = set(self._execute(query.right))
        return list(left | right)

    @staticmethod
    def _collect_terms(query: SearchQuery) -> list[str]:
        """Collect every term from a query tree for ranking.

        Walk the whole tree and gather every leaf -- like picking every
        apple off a tree instead of just the first one you see.

        Args:
            query: A parsed ``SearchQuery`` tree.

        Returns:
            A list of all term strings in the query.

        """
        if isinstance(query, TermQuery):
            return [query.term]
        # Must be AndQuery or OrQuery -- collect from both branches.
        return SearchEngine._collect_terms(query.left) + SearchEngine._collect_terms(query.right)
